(function(){
  var KEY_ROOT = "ebook-study-";
  var body = document.body;
  var dataEl = document.getElementById("site-data");
  var cfg = dataEl ? JSON.parse(dataEl.textContent) : {};
  var key = KEY_ROOT + (cfg.storageKey || "book") + "-v1";

  function load(){ try{ return JSON.parse(localStorage.getItem(key)) || {done:[],quiz:{}}; }catch(e){ return {done:[],quiz:{}}; } }
  function save(p){ localStorage.setItem(key, JSON.stringify(p)); }

  // ---------- index page ----------
  var levels = document.getElementById("levels");
  if (levels) {
    var progressText = document.getElementById("progress-text");
    var cards = [].slice.call(levels.querySelectorAll(".level"));
    var done = new Set(load().done);

    function refresh(){
      cards.forEach(function(c){
        var isDone = done.has(c.dataset.id);
        c.classList.toggle("complete", isDone);
        c.querySelector(".status").textContent = isDone ? "已通关" : "待学习";
      });
      if (progressText) progressText.innerHTML = "<b>" + done.size + "</b> / " + cards.length + " 已通关";
    }

    var activeFilter = "all";
    function applyFilter(){
      var q = (document.getElementById("search") ? document.getElementById("search").value : "").trim().toLowerCase();
      var visible = 0;
      cards.forEach(function(c){
        var okF = activeFilter === "all" || c.dataset.category === activeFilter ||
                  (activeFilter === "unfinished" && !done.has(c.dataset.id));
        var okQ = !q || (c.dataset.search || "").indexOf(q) !== -1;
        var show = okF && okQ;
        c.style.display = show ? "" : "none";
        if (show) visible++;
      });
      var empty = document.getElementById("no-results");
      if (empty) empty.hidden = visible > 0;
    }

    document.querySelectorAll("[data-filter]").forEach(function(b){
      b.addEventListener("click", function(){
        document.querySelectorAll("[data-filter]").forEach(function(x){x.classList.remove("active");});
        b.classList.add("active");
        activeFilter = b.dataset.filter;
        applyFilter();
      });
    });
    var search = document.getElementById("search");
    if (search) search.addEventListener("input", applyFilter);
    refresh();
  }

  // ---------- chapter page ----------
  var chapterId = body.getAttribute("data-chapter");
  if (chapterId) {
    var p = load();
    var quizData = document.getElementById("quiz-data");
    var quiz = quizData ? JSON.parse(quizData.textContent) : [];
    var quizKey = "quiz-" + chapterId;

    // restore quiz state
    var saved = p.quiz[quizKey] || {};
    var allRight = quiz.length > 0 && quiz.every(function(item, i){ return saved["q" + i] === true; });

    quiz.forEach(function(item, i){
      var el = document.querySelector('[data-quiz="' + i + '"]');
      if (!el) return;
      if (item.type === "choice") {
        el.querySelectorAll(".opt").forEach(function(btn){
          btn.addEventListener("click", function(){
            var correct = btn.getAttribute("data-correct") === "1";
            el.querySelectorAll(".opt").forEach(function(o){ o.disabled = true; });
            el.querySelectorAll(".opt").forEach(function(o){
              if (o.getAttribute("data-correct") === "1") o.classList.add("right");
            });
            if (!correct) btn.classList.add("wrong");
            var ex = el.querySelector(".explain"); if (ex) ex.classList.add("show");
            p = load();
            p.quiz[quizKey] = p.quiz[quizKey] || {};
            p.quiz[quizKey]["q" + i] = correct;
            if (correct && !p.done.includes(chapterId)) { p.done.push(chapterId); }
            save(p); syncUI();
          });
          if (saved["q" + i] === true || saved["q" + i] === false) {
            btn.disabled = true;
            if (btn.getAttribute("data-correct") === "1") btn.classList.add("right");
            if (saved["q" + i] === false && btn.getAttribute("data-correct") !== "1" &&
                !el.querySelector(".opt.wrong")) {
              // mark the first wrong-recorded option heuristically: highlight correct only
            }
          }
        });
        var ex = el.querySelector(".explain");
        if (ex && saved["q" + i] !== undefined) ex.classList.add("show");
      } else { // reveal
        var btn = el.querySelector(".reveal-btn");
        var ans = el.querySelector(".answer");
        if (btn && ans) btn.addEventListener("click", function(){
          ans.classList.toggle("show");
          btn.textContent = ans.classList.contains("show") ? "收起答案" : "查看参考答案";
        });
      }
    });

    // mark complete button
    var markBtn = document.getElementById("mark-done");
    function syncUI(){
      p = load();
      var isDone = p.done.includes(chapterId);
      if (markBtn){
        markBtn.classList.toggle("done", isDone);
        markBtn.textContent = isDone ? "✓ 已通关" : "标记已通关";
      }
    }
    if (markBtn) markBtn.addEventListener("click", function(){
      p = load();
      if (!p.done.includes(chapterId)) { p.done.push(chapterId); save(p); }
      syncUI();
    });
    syncUI();
  }
})();
