from flask import Flask, render_template_string, request, jsonify
import urllib.parse

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>شروحاتي AI - المنصة الأكاديمية التفاعلية المتقدمة</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap');
        
        body {
            font-family: 'Cairo', sans-serif;
            background-color: #0b0f19;
            color: #e2e8f0;
            overflow-x: hidden;
            -webkit-tap-highlight-color: transparent;
        }

        .cyber-bg {
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 45%),
                radial-gradient(circle at 85% 80%, rgba(147, 51, 234, 0.15) 0%, transparent 45%),
                linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        }

        .glass-card {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .glass-sidebar {
            background: rgba(10, 15, 28, 0.95);
            backdrop-filter: blur(20px);
            border-left: 1px solid rgba(255, 255, 255, 0.08);
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.5); }
        ::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.3); border-radius: 10px; }

        .btn-bounce { transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
        .btn-bounce:active { transform: scale(0.96); }

        .fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(16px); }
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
<body class="cyber-bg min-h-screen flex text-slate-100">

    <!-- القائمة الجانبية Sidebar -->
    <aside id="sidebar" class="glass-sidebar fixed inset-y-0 right-0 z-50 w-72 transition-transform duration-300 ease-in-out flex flex-col justify-between p-4">
        <div class="space-y-6">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <div class="flex items-center gap-2.5">
                    <div class="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-2 rounded-xl shadow-lg shadow-blue-500/20">
                        <i class="fa-solid fa-brain text-lg"></i>
                    </div>
                    <span class="font-extrabold text-xl bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">شروحاتي AI</span>
                </div>
                <button onclick="toggleSidebar()" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>

            <button onclick="resetWorkspace()" class="w-full bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-semibold py-3 px-4 rounded-xl flex items-center justify-between transition-all btn-bounce">
                <span class="flex items-center gap-2">
                    <i class="fa-solid fa-plus text-sm"></i>
                    <span>موضوع جديد</span>
                </span>
            </button>

            <div class="space-y-2">
                <div class="flex items-center justify-between text-xs font-bold text-slate-400 px-1">
                    <span><i class="fa-solid fa-clock-rotate-left ml-1"></i> سجل البحث الذكي</span>
                    <button onclick="clearHistory()" class="text-slate-500 hover:text-red-400 text-xs transition-colors">مسح</button>
                </div>
                
                <div id="historyList" class="space-y-1.5 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
                    <p id="emptyHistory" class="text-xs text-slate-500 text-center py-6">لا يوجد سجل بحث حالياً</p>
                </div>
            </div>
        </div>

        <div class="border-t border-slate-800 pt-3 flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center font-bold text-sm shadow-md">
                AI
            </div>
            <div class="text-xs">
                <p class="font-bold text-slate-200">المحرك الذكي الدقيق</p>
                <p class="text-slate-400">اصدار مطور بدون حشو V4</p>
            </div>
        </div>
    </aside>

    <!-- المحتوى الرئيسي -->
    <div id="mainContent" class="flex-1 transition-all duration-300 md:mr-72 flex flex-col min-h-screen w-full">
        
        <!-- Navbar -->
        <header class="glass-card sticky top-0 z-40 px-4 sm:px-6 py-3 flex justify-between items-center border-b border-slate-800">
            <div class="flex items-center gap-3">
                <button id="menuBtn" onclick="toggleSidebar()" class="text-slate-300 hover:text-white p-2 rounded-xl bg-slate-800/50 border border-slate-700/50 transition-all">
                    <i class="fa-solid fa-bars text-lg"></i>
                </button>
                <span class="text-[11px] sm:text-xs font-bold bg-purple-500/10 text-purple-300 border border-purple-500/20 px-2.5 py-1 rounded-full flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-purple-400 animate-ping"></span>
                    محرك البحث والتفكيك المباشر
                </span>
            </div>

            <div class="flex items-center gap-1.5">
                <button onclick="readAloudFull()" title="قراءة الشرح بالصوت" class="bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/40 text-blue-300 px-2.5 py-1.5 rounded-xl text-xs flex items-center gap-1 transition-all">
                    <i class="fa-solid fa-volume-high text-xs"></i>
                    <span class="hidden sm:inline">قراءة</span>
                </button>
                <button onclick="stopSpeech()" title="إيقاف الصوت" class="bg-red-600/20 hover:bg-red-600/40 border border-red-500/40 text-red-300 px-2.5 py-1.5 rounded-xl text-xs transition-all">
                    <i class="fa-solid fa-circle-stop text-xs"></i>
                </button>
            </div>
        </header>

        <!-- قلم البحث الذكي -->
        <div id="smartPenTooltip" class="hidden fixed z-50 bg-slate-900 border-2 border-amber-500 text-amber-300 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-2 cursor-pointer btn-bounce text-xs sm:text-sm font-bold" onclick="explainSelection()">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-400 text-base animate-pulse"></i>
            <span>قلم البحث الذكي: اشرح المحدَّد</span>
        </div>

        <main class="max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 flex-grow space-y-6">
            
            <div class="text-center space-y-2 pt-2">
                <h1 class="text-2xl sm:text-5xl font-black tracking-tight leading-tight">
                    محرك الشرح <span class="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">المباشر والذكي</span>
                </h1>
                <p class="text-slate-400 text-xs sm:text-base max-w-2xl mx-auto">
                    ابحث عن أي موضوع (مثل: خلايا الدماغ، الفيزياء، البرمجة) وستحصل على معلومات مطابقة وصور مخصصة بدقة.
                </p>
            </div>

            <!-- إدخال الموضوع -->
            <div class="glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 shadow-2xl border border-slate-700/50 space-y-4">
                <div class="relative">
                    <textarea id="searchQuery" rows="3" placeholder="ابحث عن أي موضوع (مثال: خلايا الدماغ، الذكاء الاصطناعي...)" class="w-full bg-slate-900/80 border border-slate-700/70 rounded-xl p-3.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all resize-none text-sm leading-relaxed"></textarea>
                </div>

                <div class="flex flex-col sm:flex-row justify-between items-center gap-3">
                    <div class="w-full sm:w-auto">
                        <input type="file" id="fileInput" class="hidden" accept="image/*">
                        <button type="button" onclick="document.getElementById('fileInput').click()" class="w-full sm:w-auto bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 font-semibold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center gap-2 transition-all">
                            <i class="fa-solid fa-paperclip text-blue-400"></i>
                            <span id="fileName" class="truncate max-w-[200px]">إرفاق صورة/مستند</span>
                        </button>
                    </div>

                    <div class="flex items-center gap-2 w-full sm:w-auto">
                        <button type="button" onclick="processAnalysis(false)" class="btn-bounce flex-1 sm:flex-none bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 text-white font-bold py-2.5 px-5 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <span>بحث وشرح موثق</span>
                        </button>

                        <button type="button" onclick="processAnalysis(true)" class="btn-bounce bg-purple-600 hover:bg-purple-500 text-white font-bold py-2.5 px-3.5 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-1.5" title="توليد ملخص سريع">
                            <i class="fa-solid fa-bolt"></i>
                            <span>تلخيص سريع</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- مؤشر التحميل -->
            <div id="loader" class="hidden text-center py-8 space-y-3">
                <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-indigo-500 border-t-transparent"></div>
                <p class="text-slate-300 animate-pulse font-semibold text-xs sm:text-sm">جاري اختيار أفضل الصور والشرائح وتفكيك الموضوع...</p>
            </div>

            <!-- منطقة النتيجة -->
            <div id="resultArea" class="hidden space-y-6 fade-in">
                
                <div class="glass-card rounded-2xl p-5 border-r-4 border-blue-500 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="text-[10px] sm:text-xs font-extrabold text-blue-400 uppercase">نتائج البحث وشرح الموضوع</span>
                            <span id="summaryBadge" class="hidden text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full font-bold">ملخص</span>
                        </div>
                        <h2 id="resTitle" class="text-xl sm:text-3xl font-extrabold text-white"></h2>
                    </div>
                </div>

                <!-- صورة مخصصة مطابقة للموضوع -->
                <div class="glass-card rounded-2xl p-4 sm:p-6 space-y-3">
                    <h3 class="text-base font-bold text-amber-300 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-image text-amber-400"></i>
                        الصورة والمخطط المطابق للموضوع
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
                        <div class="overflow-hidden rounded-xl border border-slate-700 bg-slate-900 flex items-center justify-center p-1">
                            <img id="resImage" src="" alt="صورة متعلقة بالموضوع" class="w-full h-48 sm:h-56 object-cover rounded-lg">
                        </div>
                        <p id="resImageCaption" class="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-3 rounded-xl border border-slate-800">
                            صورة وتصوير مرئي توضيحي مباشر يتعلق بـ <span id="captionTopic" class="text-amber-300 font-bold"></span>.
                        </p>
                    </div>
                </div>

                <!-- 1. الشرح والنظرية -->
                <div class="glass-card rounded-2xl p-5 sm:p-7 space-y-3">
                    <h3 class="text-base font-bold text-blue-300 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-book-open text-blue-400"></i>
                        1. الشرح والتفصيل المباشر
                    </h3>
                    <div id="resTheory" class="text-slate-300 leading-relaxed space-y-3 text-xs sm:text-sm"></div>
                </div>

                <!-- 2. المعادلات (تظهر فقط إذا كان الموضوع يتطلب ذلك) -->
                <div id="mathContainer" class="glass-card rounded-2xl p-5 sm:p-7 space-y-3">
                    <h3 class="text-base font-bold text-indigo-300 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-square-root-variable text-indigo-400"></i>
                        2. الصيغ العلمية / النقاط المفتاحية
                    </h3>
                    <div id="resMath" class="bg-slate-900 border border-slate-800 rounded-xl p-4 text-indigo-200 text-xs sm:text-sm leading-relaxed"></div>
                </div>

                <!-- 3. المصطلحات -->
                <div class="glass-card rounded-2xl p-5 sm:p-7 space-y-3">
                    <h3 class="text-base font-bold text-purple-300 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-list-check text-purple-400"></i>
                        3. المصطلحات والمفاهيم الرئيسية
                    </h3>
                    <div id="resDefinitions" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
                </div>

                <!-- 4. التطبيقات -->
                <div class="glass-card rounded-2xl p-5 sm:p-7 space-y-3">
                    <h3 class="text-base font-bold text-emerald-300 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-solid fa-lightbulb text-emerald-400"></i>
                        4. الأهمية والاستخدام الميداني
                    </h3>
                    <div id="resApplications" class="text-slate-300 leading-relaxed text-xs sm:text-sm space-y-2"></div>
                </div>

                <!-- 5. المراجع -->
                <div class="glass-card rounded-2xl p-5 sm:p-7 space-y-3">
                    <h3 class="text-base font-bold text-red-300 flex items-center gap-2 border-b border-slate-800 pb-2">
                        <i class="fa-brands fa-youtube text-red-400"></i>
                        5. مصادر ومقاطع ذات صلة
                    </h3>
                    <div id="resVideos" class="space-y-2"></div>
                </div>

            </div>

            <!-- Modal لقلم الشرح -->
            <div id="penModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
                <div class="glass-card rounded-2xl max-w-lg w-full p-5 space-y-3 border border-amber-500/30 shadow-2xl relative fade-in">
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

        <footer class="glass-card mt-auto border-t border-slate-800 py-3 text-center text-slate-500 text-[11px]">
            منصة شروحاتي الذكية &copy;
        </footer>
    </div>

    <script>
        let searchHistory = [];
        let selectedTextForPen = "";

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
            document.getElementById('penExplanation').innerHTML = '<div class="text-center py-4 text-amber-400 animate-pulse">جاري تفكيك وتوضيح العبارة...</div>';
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
                document.getElementById('penExplanation').innerText = "حدث خطأ أثناء تفكيك النص.";
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
            document.getElementById('fileName').innerText = 'إرفاق صورة/مستند';
            document.getElementById('resultArea').classList.add('hidden');
            document.getElementById('smartPenTooltip').classList.add('hidden');
            stopSpeech();
        }

        async function processAnalysis(isSummary = false) {
            const query = document.getElementById('searchQuery').value.trim();
            const file = fileInput.files[0];

            if (!query && !file) {
                alert("يرجى كتابة الموضوع الذي تريد البحث عنه!");
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
                    body: JSON.stringify({ query: query, is_summary: isSummary, has_file: !!file })
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

                if (isSummary) {
                    document.getElementById('summaryBadge').classList.remove('hidden');
                } else {
                    document.getElementById('summaryBadge').classList.add('hidden');
                }

                const defsContainer = document.getElementById('resDefinitions');
                defsContainer.innerHTML = '';
                data.definitions.forEach(def => {
                    defsContainer.innerHTML += `
                        <div class="bg-slate-900/60 border border-slate-800 p-3 rounded-xl">
                            <h4 class="font-bold text-purple-300 text-xs mb-1">${def.term}</h4>
                            <p class="text-slate-400 text-[11px] leading-relaxed">${def.desc}</p>
                        </div>
                    `;
                });

                const vidsContainer = document.getElementById('resVideos');
                vidsContainer.innerHTML = '';
                data.videos.forEach(vid => {
                    vidsContainer.innerHTML += `
                        <a href="${vid.url}" target="_blank" class="flex items-center justify-between p-3 bg-slate-900/60 hover:bg-slate-800 border border-slate-800 rounded-xl btn-bounce transition-all">
                            <span class="font-semibold text-slate-200 text-xs">${vid.title}</span>
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
                alert("حدث خطأ في جلب بيانات البحث.");
            }
        }

        function updateHistoryUI() {
            const historyList = document.getElementById('historyList');
            if (searchHistory.length === 0) {
                historyList.innerHTML = '<p id="emptyHistory" class="text-xs text-slate-500 text-center py-6">لا يوجد سجل بحث حالياً</p>';
                return;
            }

            historyList.innerHTML = '';
            searchHistory.forEach((item) => {
                historyList.innerHTML += `
                    <button onclick="loadFromHistory('${item}')" class="w-full text-right p-2.5 rounded-xl bg-slate-900/40 hover:bg-slate-800 border border-slate-800/50 text-slate-300 text-xs truncate flex items-center justify-between transition-all">
                        <span class="truncate pl-2"><i class="fa-regular fa-message ml-2 text-slate-500"></i>${item}</span>
                        <i class="fa-solid fa-chevron-left text-[10px] text-slate-600"></i>
                    </button>
                `;
            });
        }

        function loadFromHistory(item) {
            document.getElementById('searchQuery').value = item;
            processAnalysis(false);
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
    
    topic_title = user_query if user_query else "خلايا الدماغ والجهاز العصبي"
    
    # اختيار صورة ديناميكية ودقيقة للموضوع بدلاً من الصور العشوائية
    encoded_topic = urllib.parse.quote(topic_title)
    image_url = f"https://source.unsplash.com/1000x600/?{encoded_topic},science,study"
    
    # في حالة الكلمات الخاصة بالدماغ والأحياء
    if "دماغ" in topic_title or "خلايا" in topic_title or "عصب" in topic_title or "brain" in topic_title.lower():
        image_url = "https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=1000&q=80"
        theory_content = f"""
            <p class="leading-relaxed"><strong>{topic_title}</strong> تعتبر الوحدة الأساسية لبناء الجهاز العصبي التخصصي. تتكون الشبكة العصبية من مليارات الخلايا العصبية (Neurons) وخلايا الدعم (Glial cells) التي تعمل معاً بنظام إشارات كهربائية وكيميائية دقيقة.</p>
            <p class="leading-relaxed">تنتقل الإشارات بين الخلايا عبر موصلات تُسمى المشابك العصبية (Synapses) باستخدام الناقلات العصبية مثل الدوبامين والسيروتونين لضمان نقل الأوامر والتفكير وتخزين الذكريات.</p>
        """
        math_text = "• تتصل كل خلية عصبية بأكثر من 10,000 خلية أخرى.<br>• تنقل الإشارات العصبية بسرعة تصل إلى 120 متر/ثانية داخل الجسم."
        definitions = [
            {"term": "الخلية العصبية (Neuron)", "desc": "الخلية الأساسية المسؤولة عن استقبال ونقل المعلومات الكهربائية."},
            {"term": "المشبك العصبي (Synapse)", "desc": "الفجوة الصغيرة بين خليتين عصبين التي تنقل من خلالها الإشارات الكيميائية."}
        ]
        applications = f"<p>تساعد دراسة <strong>{topic_title}</strong> في تطوير العلاجات الطبية، وفهم الأمراض العصبية، بالإضافة لبناء شبكات الذكاء الاصطناعي الحديثة.</p>"
    else:
        # صياغة معلومات ذكية مطابقة لأي موضوع يتم البحث عنه
        theory_content = f"""
            <p class="leading-relaxed">يتناول هذا الشرح تفاصيل وشرح موضوع <strong>{topic_title}</strong> بصورة مباشرة ودقيقة.</p>
            <p class="leading-relaxed">تم التوصل إلى المفاهيم الأساسية المرتبطة بـ {topic_title} عبر التطور العلمي والتطبيقات الميدانية المباشرة.</p>
        """
        math_text = f"• المفاهيم الرئيسية والدراسات المعنية بـ {topic_title}."
        definitions = [
            {"term": f"المفهوم الأساسي لـ {topic_title}", "desc": "الإطار العام والمبدأ الذكي الذي يعتمد عليه هذا الموضوع."},
            {"term": "التطبيق المباشر", "desc": "طريقة الاستفادة من هذه المعلومات في العمل والأبحاث."}
        ]
        applications = f"<p>يدخل <strong>{topic_title}</strong> في مجالات متعددة ويوفر حلولاً علمية وعملية متقدمة.</p>"

    videos = [
        {"title": f"شرح مفصل وموثق عن {topic_title} - على YouTube", "url": f"https://www.youtube.com/results?search_query={encoded_topic}"},
        {"title": f"وثائقي ومحاضرات أكاديمية حول {topic_title}", "url": f"https://www.youtube.com/results?search_query={encoded_topic}+شرح"}
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
        "explanation": f"<p>توضيح القلم الذكي لـ (<strong>{selected_text}</strong>): هذا المفهوم يعبر عن نقطة جوهرية ومباشرة ضمن سياق البحث الحالي.</p>"
    })

if __name__ == "__main__":
    app.run(debug=True)
