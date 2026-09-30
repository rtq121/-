from flask import Flask, render_template_string, request, jsonify
import urllib.parse

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>شروحاتي AI - منصة المراجعة الجامعية الذكية</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap');
        
        body {
            font-family: 'Cairo', sans-serif;
            background-color: #0f172a;
            color: #f1f5f9;
            overflow-x: hidden;
            -webkit-tap-highlight-color: transparent;
        }

        .gemini-card {
            background: #1e293b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1.25rem;
        }

        .glass-sidebar {
            background: #0f172a;
            border-left: 1px solid rgba(255, 255, 255, 0.08);
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 10px; }

        .btn-bounce { transition: all 0.2s ease; }
        .btn-bounce:active { transform: scale(0.96); }

        .fade-in { animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            #mainContent { margin-right: 0 !important; }
            #sidebar { transform: translateX(100%); }
            #sidebar.open { transform: translateX(0); }
            
            #smartPenTooltip {
                position: fixed !important;
                bottom: 20px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                top: auto !important;
                width: 90% !important;
                max-width: 380px !important;
                justify-content: center !important;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.8), 0 0 15px rgba(245, 158, 11, 0.4) !important;
            }
        }
    </style>
</head>
<body class="min-h-screen flex text-slate-100 bg-slate-900">

    <!-- القائمة الجانبية Sidebar -->
    <aside id="sidebar" class="glass-sidebar fixed inset-y-0 right-0 z-50 w-72 transition-transform duration-300 ease-in-out flex flex-col justify-between p-4">
        <div class="space-y-6">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <div class="flex items-center gap-2.5">
                    <div class="bg-blue-600 text-white p-2 rounded-xl">
                        <i class="fa-solid fa-graduation-cap text-lg"></i>
                    </div>
                    <span class="font-extrabold text-xl text-white">شروحاتي AI</span>
                </div>
                <button onclick="toggleSidebar()" class="text-slate-400 hover:text-white p-1 rounded-lg md:hidden">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>

            <button onclick="resetWorkspace()" class="w-full bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-semibold py-3 px-4 rounded-xl flex items-center justify-between transition-all btn-bounce">
                <span class="flex items-center gap-2">
                    <i class="fa-solid fa-plus text-sm"></i>
                    <span>سؤال / مراجعة جديدة</span>
                </span>
            </button>

            <div class="space-y-2">
                <div class="flex items-center justify-between text-xs font-bold text-slate-400 px-1">
                    <span><i class="fa-solid fa-clock-rotate-left ml-1"></i> السجل والأبحاث</span>
                    <button onclick="clearHistory()" class="text-slate-500 hover:text-red-400 text-xs">مسح</button>
                </div>
                
                <div id="historyList" class="space-y-1.5 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
                    <p id="emptyHistory" class="text-xs text-slate-500 text-center py-6">لا يوجد سجل حالياً</p>
                </div>
            </div>
        </div>

        <div class="border-t border-slate-800 pt-3 flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center font-bold text-sm">
                🎓
            </div>
            <div class="text-xs">
                <p class="font-bold text-slate-200">المُراجع الأكاديمي الجامعي</p>
                <p class="text-slate-400">نمط الذكاء التفاعلي</p>
            </div>
        </div>
    </aside>

    <!-- المحتوى الرئيسي -->
    <div id="mainContent" class="flex-1 transition-all duration-300 md:mr-72 flex flex-col min-h-screen w-full">
        
        <!-- Navbar -->
        <header class="gemini-card rounded-none border-x-0 border-t-0 sticky top-0 z-40 px-4 sm:px-6 py-3 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <button id="menuBtn" onclick="toggleSidebar()" class="text-slate-300 hover:text-white p-2 rounded-xl bg-slate-800 border border-slate-700 md:hidden">
                    <i class="fa-solid fa-bars text-lg"></i>
                </button>
                <span class="text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-full flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
                    محرك الشرح والمراجعة للاختبارات
                </span>
            </div>

            <div class="flex items-center gap-2">
                <button onclick="readAloudFull()" title="قراءة الشرح بالصوت" class="bg-slate-800 hover:bg-slate-700 text-blue-400 px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 border border-slate-700">
                    <i class="fa-solid fa-volume-high"></i>
                    <span class="hidden sm:inline">قراءة صوتية</span>
                </button>
                <button onclick="stopSpeech()" title="إيقاف الصوت" class="bg-slate-800 hover:bg-slate-700 text-red-400 px-2.5 py-1.5 rounded-xl text-xs border border-slate-700">
                    <i class="fa-solid fa-circle-stop"></i>
                </button>
            </div>
        </header>

        <!-- قلم البحث الذكي -->
        <div id="smartPenTooltip" class="hidden fixed z-50 bg-slate-900 border-2 border-amber-500 text-amber-300 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-2 cursor-pointer btn-bounce text-xs sm:text-sm font-bold" onclick="explainSelection()">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-400 text-base animate-pulse"></i>
            <span>قلم البحث الذكي: اشرح المحدَّد</span>
        </div>

        <main class="max-w-4xl mx-auto w-full px-4 sm:px-6 py-8 flex-grow space-y-6">
            
            <div class="text-center space-y-2">
                <h1 class="text-2xl sm:text-4xl font-extrabold text-white">
                    كيف يمكنني مساعدتك في <span class="text-blue-400">دراستك اليوم؟</span>
                </h1>
                <p class="text-slate-400 text-xs sm:text-sm">
                    اكتب أي سؤال أو مفهوم للحصول على شرح شامل ومراجعة للأختبارات الأكاديمية.
                </p>
            </div>

            <!-- خيار التلخيص العالي والشريط الرئيسي -->
            <div class="gemini-card p-4 sm:p-5 shadow-xl space-y-4">
                
                <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                    <span class="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                        <i class="fa-solid fa-sliders text-blue-400"></i> وضع الإجابة:
                    </span>
                    <div class="flex items-center gap-2">
                        <button type="button" onclick="setSummaryMode(false)" id="btnFullMode" class="bg-blue-600 text-white font-bold py-1.5 px-3.5 rounded-xl text-xs border border-blue-500 transition-all">
                            <i class="fa-solid fa-book-open ml-1"></i> شرح تفصيلي ومراجعة
                        </button>
                        <button type="button" onclick="setSummaryMode(true)" id="btnSummaryMode" class="bg-slate-800 hover:bg-slate-700 text-purple-300 font-bold py-1.5 px-3.5 rounded-xl text-xs border border-slate-700 transition-all">
                            <i class="fa-solid fa-bolt ml-1"></i> تلخيص سريع ومكثف
                        </button>
                    </div>
                </div>

                <div class="relative">
                    <textarea id="searchQuery" rows="3" placeholder="اكتب سؤالك أو موضوعك هنا... مثال: ما هو قانون أوم؟ أو اشرح الجهاز العصبي..." class="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl p-3.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all resize-none text-sm leading-relaxed"></textarea>
                </div>

                <div class="flex flex-col sm:flex-row justify-between items-center gap-3">
                    <div class="w-full sm:w-auto">
                        <input type="file" id="fileInput" class="hidden" accept="image/*">
                        <button type="button" onclick="document.getElementById('fileInput').click()" class="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-semibold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center gap-2">
                            <i class="fa-solid fa-paperclip text-blue-400"></i>
                            <span id="fileName" class="truncate max-w-[200px]">إرفاق صورة / مستند</span>
                        </button>
                    </div>

                    <button type="button" onclick="processAnalysis()" class="btn-bounce w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-7 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20">
                        <i class="fa-solid fa-sparkles"></i>
                        <span id="submitBtnText">عرض الإجابة والمراجعة</span>
                    </button>
                </div>
            </div>

            <!-- مؤشر التحميل -->
            <div id="loader" class="hidden text-center py-8 space-y-3">
                <div class="inline-block animate-spin rounded-full h-9 w-9 border-4 border-blue-500 border-t-transparent"></div>
                <p class="text-slate-300 animate-pulse font-semibold text-xs sm:text-sm">جاري تحليل سؤالك وإعداد المراجعة الشاملة...</p>
            </div>

            <!-- منطقة النتيجة -->
            <div id="resultArea" class="hidden space-y-5 fade-in">
                
                <!-- عنوان النتيجة -->
                <div class="gemini-card p-5 border-r-4 border-blue-500 flex justify-between items-center">
                    <div>
                        <span id="summaryBadge" class="hidden text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2.5 py-0.5 rounded-full font-bold mb-2 inline-block">⚡ تلخيص سريع للاختبار</span>
                        <h2 id="resTitle" class="text-xl sm:text-2xl font-black text-white"></h2>
                    </div>
                </div>

                <!-- الصورة التوضيحية -->
                <div class="gemini-card p-4 sm:p-5 space-y-3">
                    <h3 class="text-sm font-bold text-amber-400 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-image"></i>
                        التوضيح المرئي
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
                        <div class="overflow-hidden rounded-xl border border-slate-700 bg-slate-900 flex items-center justify-center p-1">
                            <img id="resImage" src="" alt="صورة توضيحية" class="w-full h-52 object-cover rounded-lg">
                        </div>
                        <p id="resImageCaption" class="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                            صورة وتوضيح مرئي مباشر يخص الموضوع المترابط: <span id="captionTopic" class="text-blue-400 font-bold"></span>.
                        </p>
                    </div>
                </div>

                <!-- الشرح والأجوبة -->
                <div class="gemini-card p-5 sm:p-6 space-y-3">
                    <h3 class="text-sm font-bold text-blue-400 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-graduation-cap"></i>
                        1. الشرح والإجابة المباشرة
                    </h3>
                    <div id="resTheory" class="text-slate-300 leading-relaxed space-y-3 text-xs sm:text-sm"></div>
                </div>

                <!-- النقاط المفتاحية -->
                <div id="mathContainer" class="gemini-card p-5 sm:p-6 space-y-3">
                    <h3 class="text-sm font-bold text-indigo-400 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-key"></i>
                        2. حقائق وملاحظات سريعة للامتحان (Exam Key Points)
                    </h3>
                    <div id="resMath" class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs sm:text-sm leading-relaxed"></div>
                </div>

                <!-- المصطلحات المفتاحية -->
                <div class="gemini-card p-5 sm:p-6 space-y-3">
                    <h3 class="text-sm font-bold text-purple-400 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-list-check"></i>
                        3. مصطلحات وتعاريف هامة
                    </h3>
                    <div id="resDefinitions" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
                </div>

                <!-- أسئلة المراجعة -->
                <div class="gemini-card p-5 sm:p-6 space-y-3">
                    <h3 class="text-sm font-bold text-emerald-400 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-circle-question"></i>
                        4. أسئلة امتحانات وتطبيقات متوقعة
                    </h3>
                    <div id="resApplications" class="text-slate-300 leading-relaxed text-xs sm:text-sm space-y-2"></div>
                </div>

                <!-- الفيديوهات -->
                <div class="gemini-card p-5 sm:p-6 space-y-3">
                    <h3 class="text-sm font-bold text-red-400 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-brands fa-youtube"></i>
                        5. دروس وفيديوهات توضيحية ذات صلة
                    </h3>
                    <div id="resVideos" class="space-y-2"></div>
                </div>

            </div>

            <!-- Modal لقلم الشرح -->
            <div id="penModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
                <div class="gemini-card max-w-lg w-full p-5 space-y-3 border border-amber-500/30 shadow-2xl relative fade-in">
                    <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                        <div class="flex items-center gap-2 text-amber-400 font-bold text-xs sm:text-sm">
                            <i class="fa-solid fa-wand-magic-sparkles"></i>
                            <span>قلم الشرح الذكي</span>
                        </div>
                        <button onclick="closePenModal()" class="text-slate-400 hover:text-white p-1">
                            <i class="fa-solid fa-xmark text-lg"></i>
                        </button>
                    </div>
                    <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800 text-xs text-amber-200/80 italic">
                        " <span id="penSelectedText"></span> "
                    </div>
                    <div id="penExplanation" class="text-slate-200 text-xs sm:text-sm leading-relaxed space-y-2 max-h-60 overflow-y-auto pr-1"></div>
                    <div class="flex justify-end pt-2">
                        <button onclick="closePenModal()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-1.5 rounded-xl text-xs">إغلاق</button>
                    </div>
                </div>
            </div>

        </main>

        <footer class="text-center py-4 text-slate-500 text-xs border-t border-slate-800 mt-auto">
            منصة شروحاتي AI للمراجعة الأكاديمية &copy;
        </footer>
    </div>

    <script>
        let searchHistory = [];
        let selectedTextForPen = "";
        let isSummaryMode = false;

        function setSummaryMode(isSummary) {
            isSummaryMode = isSummary;
            const btnFull = document.getElementById('btnFullMode');
            const btnSum = document.getElementById('btnSummaryMode');
            
            if (isSummary) {
                btnSum.className = "bg-purple-600 text-white font-bold py-1.5 px-3.5 rounded-xl text-xs border border-purple-500 transition-all";
                btnFull.className = "bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold py-1.5 px-3.5 rounded-xl text-xs border border-slate-700 transition-all";
                document.getElementById('submitBtnText').innerText = "عرض الملخص السريع";
            } else {
                btnFull.className = "bg-blue-600 text-white font-bold py-1.5 px-3.5 rounded-xl text-xs border border-blue-500 transition-all";
                btnSum.className = "bg-slate-800 hover:bg-slate-700 text-purple-300 font-bold py-1.5 px-3.5 rounded-xl text-xs border border-slate-700 transition-all";
                document.getElementById('submitBtnText').innerText = "عرض الإجابة والمراجعة";
            }
        }

        function readText(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const cleanText = text.replace(/<[^>]*>?/gm, '');
                const utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.lang = 'ar-SA';
                utterance.rate = 0.95;
                window.speechSynthesis.speak(utterance);
            }
        }

        function readAloudFull() {
            const fullText = document.getElementById('resTitle').innerText + ". " + 
                             document.getElementById('resTheory').innerText;
            readText(fullText);
        }

        function stopSpeech() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }

        function handleTextSelection() {
            setTimeout(() => {
                const selection = window.getSelection();
                const text = selection.toString().trim();
                const tooltip = document.getElementById('smartPenTooltip');

                if (text.length > 3 && document.getElementById('resultArea').contains(selection.anchorNode)) {
                    selectedTextForPen = text;
                    if (window.innerWidth > 768) {
                        try {
                            const range = selection.getRangeAt(0);
                            const rect = range.getBoundingClientRect();
                            tooltip.style.top = `${rect.top - 45}px`;
                            tooltip.style.left = `${rect.left + (rect.width / 2) - 80}px`;
                        } catch(e) {}
                    }
                    tooltip.classList.remove('hidden');
                } else {
                    if (!selectedTextForPen) {
                        tooltip.classList.add('hidden');
                    }
                }
            }, 100);
        }

        document.addEventListener('selectionchange', handleTextSelection);
        document.addEventListener('mouseup', handleTextSelection);
        document.addEventListener('touchend', handleTextSelection);

        async function explainSelection() {
            document.getElementById('smartPenTooltip').classList.add('hidden');
            document.getElementById('penSelectedText').innerText = selectedTextForPen;
            document.getElementById('penExplanation').innerHTML = '<div class="text-center py-4 text-amber-400 animate-pulse">جاري تفكيك النص وتبسيطه...</div>';
            document.getElementById('penModal').classList.remove('hidden');

            try {
                const response = await fetch('/explain_pen', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ selection: selectedTextForPen })
                });
                const data = await response.json();
                document.getElementById('penExplanation').innerHTML = data.explanation;
            } catch (err) {
                document.getElementById('penExplanation').innerText = "حدث خطأ أثناء تحليل النص المترجم.";
            } finally {
                selectedTextForPen = "";
            }
        }

        function closePenModal() {
            document.getElementById('penModal').classList.add('hidden');
            stopSpeech();
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
            sidebar.classList.toggle('translate-x-0');
        }

        const fileInput = document.getElementById('fileInput');
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                document.getElementById('fileName').innerText = "مرفق: " + e.target.files[0].name;
            }
        });

        function resetWorkspace() {
            document.getElementById('searchQuery').value = '';
            document.getElementById('fileInput').value = '';
            document.getElementById('fileName').innerText = 'إرفاق صورة / مستند';
            document.getElementById('resultArea').classList.add('hidden');
            document.getElementById('smartPenTooltip').classList.add('hidden');
            stopSpeech();
        }

        async function processAnalysis() {
            const query = document.getElementById('searchQuery').value.trim();
            const file = fileInput.files[0];

            if (!query && !file) {
                alert("يرجى كتابة السؤال أو الموضوع الذي ترغب بمراجعته!");
                return;
            }

            document.getElementById('loader').classList.remove('hidden');
            document.getElementById('resultArea').classList.add('hidden');
            document.getElementById('smartPenTooltip').classList.add('hidden');
            stopSpeech();

            try {
                const response = await fetch('/analyze', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, is_summary: isSummaryMode, has_file: !!file })
                });
                const data = await response.json();

                document.getElementById('loader').classList.add('hidden');

                if(query && !searchHistory.includes(query)) {
                    searchHistory.unshift(query);
                    updateHistoryUI();
                }

                document.getElementById('resTitle').innerText = data.title;
                document.getElementById('captionTopic').innerText = data.title;
                document.getElementById('resTheory').innerHTML = data.theory;
                document.getElementById('resMath').innerHTML = data.math;
                document.getElementById('resApplications').innerHTML = data.applications;
                document.getElementById('resImage').src = data.image_url;

                if (isSummaryMode) {
                    document.getElementById('summaryBadge').classList.remove('hidden');
                } else {
                    document.getElementById('summaryBadge').classList.add('hidden');
                }

                const defsContainer = document.getElementById('resDefinitions');
                defsContainer.innerHTML = '';
                data.definitions.forEach(def => {
                    defsContainer.innerHTML += `
                        <div class="bg-slate-900/90 border border-slate-800 p-3 rounded-xl">
                            <h4 class="font-bold text-purple-300 text-xs mb-1">${def.term}</h4>
                            <p class="text-slate-400 text-[11px] leading-relaxed">${def.desc}</p>
                        </div>
                    `;
                });

                const vidsContainer = document.getElementById('resVideos');
                vidsContainer.innerHTML = '';
                data.videos.forEach(vid => {
                    vidsContainer.innerHTML += `
                        <a href="${vid.url}" target="_blank" class="flex items-center justify-between p-3 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl transition-all">
                            <span class="font-semibold text-slate-200 text-xs"><i class="fa-brands fa-youtube text-red-500 ml-2"></i>${vid.title}</span>
                            <i class="fa-solid fa-arrow-up-right-from-square text-slate-500 text-xs"></i>
                        </a>
                    `;
                });

                const resultArea = document.getElementById('resultArea');
                resultArea.classList.remove('hidden');
                
                if (window.MathJax) {
                    MathJax.typesetPromise();
                }

                resultArea.scrollIntoView({ behavior: 'smooth' });

            } catch (error) {
                document.getElementById('loader').classList.add('hidden');
                alert("حدث خطأ أثناء تحضير الإجابة والمراجعة.");
            }
        }

        function updateHistoryUI() {
            const historyList = document.getElementById('historyList');
            if (searchHistory.length === 0) {
                historyList.innerHTML = '<p id="emptyHistory" class="text-xs text-slate-500 text-center py-6">لا يوجد سجل حالياً</p>';
                return;
            }

            historyList.innerHTML = '';
            searchHistory.forEach((item) => {
                historyList.innerHTML += `
                    <button onclick="loadFromHistory('${item}')" class="w-full text-right p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs truncate flex items-center justify-between transition-all">
                        <span class="truncate pl-2"><i class="fa-regular fa-bookmark ml-2 text-blue-400"></i>${item}</span>
                        <i class="fa-solid fa-chevron-left text-[10px] text-slate-600"></i>
                    </button>
                `;
            });
        }

        function loadFromHistory(item) {
            document.getElementById('searchQuery').value = item;
            processAnalysis();
        }

        function clearHistory() {
            searchHistory = [];
            updateHistoryUI();
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/analyze", methods=["POST"])
def analyze_page():
    req_data = request.get_json() or {}
    user_query = req_data.get("query", "").strip()
    is_summary = req_data.get("is_summary", False)
    
    topic_title = user_query if user_query else "مراجعة موضوع عام"
    encoded_topic = urllib.parse.quote(topic_title)

    q_lower = topic_title.lower()

    # صور عشوائية متناسبة
    if any(k in q_lower for k in ["عظم", "عظام", "هيكل", "جسم", "bone", "skeleton"]):
        image_url = "https://images.unsplash.com/photo-1530210124550-912dc1381cb8?auto=format&fit=crop&w=1000&q=80"
    elif any(k in q_lower for k in ["دماغ", "عصب", "brain", "neuron", "قلب"]):
        image_url = "https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=1000&q=80"
    elif any(k in q_lower for k in ["فيزياء", "كهرباء", "قانون", "امتحان", "رياضيات", "حساب"]):
        image_url = "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=1000&q=80"
    else:
        image_url = "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1000&q=80"

    # المحتوى التفاعلي الديناميكي بناءً على السؤال المكتوب
    if is_summary:
        theory_content = f"""
            <div class="p-3.5 bg-purple-950/40 border border-purple-500/30 rounded-xl space-y-2 text-xs sm:text-sm">
                <p class="font-bold text-purple-300">⚡ ملخص مكثف وسريع لموضوع: {topic_title}</p>
                <p>• <strong>النقطة الأساسية:</strong> يدور هذا الموضوع حول فهم العناصر الرئيسية المكونة لـ ({topic_title}) وكيفية ربطها بالمفاهيم الأساسية.</p>
                <p>• <strong>التركيز للامتحان:</strong> التركيز الأهم في الاختبارات هو التمييز بين الخصائص والتطبيقات المباشرة المتعلقة بـ {topic_title}.</p>
            </div>
        """
    else:
        theory_content = f"""
            <p class="leading-relaxed">عند دراسة موضوع <strong>"{topic_title}"</strong>، يتم مناقشة الأساس الأكاديمي والتطبيقات المرتبطة به ضمن المقرر الدراسي.</p>
            <p class="leading-relaxed mt-2">يتطلب استيعاب هذا الموضوع التركيز على النقاط التالية:</p>
            <ul class="list-disc list-inside space-y-1.5 text-slate-300 my-2 pr-2">
                <li>المفاهيم والنظريات الأساسية المرتبطة بـ {topic_title}.</li>
                <li>العوامل والأسباب المباشرة التي تؤثر في تحليل وتحضير {topic_title}.</li>
                <li>أوجه المقارنة الشائعة التي ترد في أسئلة الامتحانات النصفية والنهائية.</li>
            </ul>
        """

    math_text = f"""
        • <strong>المحور الأول:</strong> فهم التعاريف المباشرة المترتبة على موضوع {topic_title}.<br>
        • <strong>المحور الثاني:</strong> الربط بين المعطيات والنتائج في المسائل والأسئلة المتعلقة بـ {topic_title}.<br>
        • <strong>تنبيه للاختبار:</strong> انتبه للتفاصيل الصغيرة والتسميات العلمية أثناء حل أسئلة {topic_title}.
    """

    definitions = [
        {"term": f"المفهوم الرئيسي لـ {topic_title}", "desc": "التعريف الأكاديمي المعتمد والمحوري في أوراق المراجعة والامتحانات."},
        {"term": "التطبيق العلمي", "desc": f"كيفية استغلال مفاهيم {topic_title} في حل المسائل والأسئلة العملية."}
    ]

    applications = f"""
        <p class="font-semibold text-emerald-300">سؤال امتحان متوقع حول ({topic_title}):</p>
        <p class="text-slate-300 mt-1">س: اشرح أو علل الأهمية والوظيفة الأساسية المتعلقة بـ {topic_title}؟</p>
        <p class="text-slate-400 text-xs mt-1 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">💡 <strong>إرشاد الإجابة:</strong> قم بذكر التعريف الرئيسي أولاً، ثم اذكر نقطتين من الخصائص أو الوظائف المدعومة بالجدول أو المعادلة.</p>
    """

    videos = [
        {"title": f"شرح ومراجعة شاملة لـ ({topic_title}) - يوتيوب", "url": f"https://www.youtube.com/results?search_query={encoded_topic}"},
        {"title": f"أسئلة امتحانات وتدريبات وحلول حول ({topic_title})", "url": f"https://www.youtube.com/results?search_query={encoded_topic}+شرح+اختبار"}
    ]

    return jsonify({
        "title": topic_title,
        "theory": theory_content,
        "math": math_text,
        "definitions": definitions,
        "applications": applications,
        "videos": videos,
        "image_url": image_url
    })

@app.route("/explain_pen", methods=["POST"])
def explain_pen():
    req_data = request.get_json() or {}
    selected_text = req_data.get("selection", "")
    return jsonify({
        "explanation": f"<p class='leading-relaxed'>تفكيك وشرح عبارة (<strong>{selected_text}</strong>):</p><p class='text-slate-300 mt-1'>هذه الجزئية تشير إلى المفهوم المفتاحي الذي يربط بين النظرية والتطبيق في السؤال، ويُنصح بحفظ المصطلح ومراجعة تطبيقه في الامتحانات.</p>"
    })

if __name__ == "__main__":
    app.run(debug=True)
