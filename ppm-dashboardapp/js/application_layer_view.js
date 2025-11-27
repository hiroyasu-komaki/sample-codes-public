/**
 * Application Layer Overview - Full Dynamic Vanilla JS
 * JSON data → Full UI generation (Config対応版)
 * primary_projects.json と application_list.json を使用
 */

let currentLanguage = window.APP_CONFIG?.defaultLanguage || 'ja';
let appData = {
    projects: null,
    applications: null
};
const config = window.APP_CONFIG || {};
const i18n = window.I18N || {};

/** 安全なテキスト取得関数 */
function getTextSafe(lang, path) {
    if (window.getText) {
        return window.getText(lang, path);
    }
    // フォールバック: パスの最後の部分を返す
    const parts = path.split('.');
    return parts[parts.length - 1];
}

/** 複数のJSONファイルをロード */
async function loadApplicationData() {
    try {
        // 1. YAML設定を読み込み
        if (window.loadConfig) {
            await window.loadConfig();
        }
        
        // 2. データパスを取得
        const projectsPath = (window.getDataPath && window.getDataPath('primary_projects')) || '../data/primary_projects.json';
        const appsPath = (window.getDataPath && window.getDataPath('application_list')) || '../data/application_list.json';
        
        // 3. 2つのJSONファイルを並列で読み込み
        const [projectsData, applicationsData] = await Promise.all([
            fetchJSON(projectsPath),
            fetchJSON(appsPath)
        ]);
        
        // 4. データをマージ
        appData = {
            projects: projectsData.projects,
            applications: applicationsData.applications
        };
        
        initializeApp();
    } catch (e) {
        console.error('データ読み込み失敗:', e);
        const errorMsg = (window.getText && window.getText(currentLanguage, 'applicationLayerView.messages.loadError')) 
            || 'アプリケーションデータの読み込みに失敗しました。';
        showError(errorMsg);
    }
}

/** JSONファイルをフェッチする共通関数 */
async function fetchJSON(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status} for ${url}`);
    return await response.json();
}

/** エラー表示 */
function showError(msg) {
    const main = document.querySelector('main');
    const errorMsg = msg || getTextSafe(currentLanguage, 'applicationLayerView.messages.loadError');
    main.innerHTML = `
        <div class="bg-red-50 p-6 border border-red-200 rounded-lg text-center text-red-700 font-medium">
            ${errorMsg}
        </div>
    `;
}

/** 初期化 */
function initializeApp() {
    if (!appData.projects || !appData.applications) return;

    renderProjectList();
    renderApplicationGrid();
    loadLanguagePreference();
}

/* ======================================================
   Sidebar: プロジェクト一覧
   ====================================================== */
function renderProjectList() {
    const list = document.querySelector('.project-list');
    if (!list) return;
    
    list.innerHTML = '';

    appData.projects.forEach(project => {
        const li = document.createElement('li');
        const preset = config.stylePresets?.projectItem || {
            base: 'project-item p-3 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-l-transparent bg-gray-50',
            hover: 'hover:bg-gray-100 hover:border-l-gradient-start hover:translate-x-1',
            active: 'active bg-gradient-to-br from-[rgba(102,126,234,0.1)] to-[rgba(118,75,162,0.1)] font-semibold'
        };
        
        li.className = `${preset.base} ${preset.hover}`;
        li.dataset.project = project.id;

        li.innerHTML = `
            <div class="project-name text-sm text-gray-800 mb-1">
                <span class="lang-ja">${project.nameJA}</span>
                <span class="lang-en">${project.nameEN}</span>
            </div>
            <div class="project-status text-xs text-gray-500">
                <span class="lang-ja">${project.statusJA} - ${project.progress}%</span>
                <span class="lang-en">${project.statusEN} - ${project.progress}%</span>
            </div>
        `;

        li.addEventListener('click', () => selectProject(project.id));
        list.appendChild(li);
    });
}

/* ======================================================
   Main: アプリケーション一覧（カード生成）
   ====================================================== */
function renderApplicationGrid() {
    const grid = document.querySelector('.app-grid');
    if (!grid) return;
    
    grid.innerHTML = '';

    appData.applications.forEach(app => {
        const card = createApplicationCard(app);
        grid.appendChild(card);
    });
}

/** アプリカード生成 */
function createApplicationCard(app) {
    const eolColors = config.eolColors || {
        critical: { bg: 'bg-red-500', text: 'text-red-700', hex: '#ef4444' },
        warning: { bg: 'bg-amber-500', text: 'text-amber-700', hex: '#f59e0b' },
        safe: { bg: 'bg-green-500', text: 'text-green-700', hex: '#10b981' },
        unknown: { bg: 'bg-gray-400', text: 'text-gray-700', hex: '#9ca3af' }
    };
    
    const categoryColors = config.categoryColors || {
        default: 'bg-blue-100 text-blue-700'
    };
    
    const eolColor = eolColors[app.eolStatus] || eolColors.unknown;
    
    const cardPreset = config.stylePresets?.card || {
        base: 'relative bg-gray-50 p-5 rounded-xl border-2 border-gray-200 transition-all duration-300',
        hover: 'hover:shadow-lg hover:-translate-y-1',
        highlighted: 'bg-gradient-to-br from-amber-400/15 to-amber-500/15 border-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.5)]'
    };

    const card = document.createElement('div');
    card.className = `app-card ${cardPreset.base} ${cardPreset.hover}`;
    card.dataset.projects = app.projects.join(' ');

    card.innerHTML = `
        <div class="eol-badge absolute -top-2 -right-2 w-4 h-4 rounded-full border-2 border-white ${eolColor.bg}"
             title="${app.eolDate} / ${app.eolDateEN}"></div>

        <div class="app-icon text-3xl mb-3">${app.icon}</div>

        <div class="app-name text-base font-semibold text-gray-800 mb-1.5">
            <span class="lang-ja">${app.nameJA}</span>
            <span class="lang-en">${app.nameEN}</span>
        </div>

        <div class="app-category text-xs text-gray-500 mb-3">
            <span class="lang-ja">${app.categoryJA}</span>
            <span class="lang-en">${app.categoryEN}</span>
        </div>

        <div class="app-tags flex flex-wrap gap-1.5">
            ${app.tags
                .map(
                    tag =>
                        `<span class="app-tag inline-block px-2 py-0.5 ${categoryColors.default} rounded text-[10px] font-medium">${tag}</span>`
                )
                .join('')}
        </div>
    `;
    return card;
}

/* ======================================================
   Project selection / highlight logic
   ====================================================== */
function selectProject(projectId) {
    const projectPreset = config.stylePresets?.projectItem || {
        base: 'project-item p-3 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-l-transparent bg-gray-50',
        hover: 'hover:bg-gray-100 hover:border-l-gradient-start hover:translate-x-1',
        active: 'active bg-gradient-to-br from-[rgba(102,126,234,0.1)] to-[rgba(118,75,162,0.1)] font-semibold'
    };
    
    const cardPreset = config.stylePresets?.card || {
        base: 'relative bg-gray-50 p-5 rounded-xl border-2 border-gray-200 transition-all duration-300',
        hover: 'hover:shadow-lg hover:-translate-y-1',
        highlighted: 'bg-gradient-to-br from-amber-400/15 to-amber-500/15 border-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.5)]'
    };
    
    // Sidebar project highlight reset
    document.querySelectorAll('.project-item').forEach(item => {
        // activeクラスのみを削除（baseとhoverは保持）
        item.className = `${projectPreset.base} ${projectPreset.hover}`;
    });

    // App highlight reset
    document.querySelectorAll('.app-card').forEach(card => {
        card.className = `app-card ${cardPreset.base} ${cardPreset.hover}`;
    });

    if (projectId) {
        // Sidebar highlight
        const selectedItem = document.querySelector(`[data-project="${projectId}"]`);
        if (selectedItem) {
            selectedItem.className = `${projectPreset.base} ${projectPreset.hover} ${projectPreset.active}`;
        }

        // Application highlight
        document.querySelectorAll('.app-card').forEach(card => {
            const projects = card.dataset.projects.split(' ');
            if (projects.includes(projectId)) {
                card.className = `app-card ${cardPreset.base} ${cardPreset.hover} ${cardPreset.highlighted} highlight-pulse`;
            }
        });

        // Title update
        const project = appData.projects.find(p => p.id === projectId);
        const titleSpan = document.getElementById('selectedProject');

        if (project && titleSpan) {
            titleSpan.textContent =
                currentLanguage === 'ja'
                    ? ` - ${project.nameJA}`
                    : ` - ${project.nameEN}`;
        }
    } else {
        const titleSpan = document.getElementById('selectedProject');
        if (titleSpan) {
            titleSpan.textContent = '';
        }
    }
}

/** 選択解除 */
function clearSelection() {
    selectProject(null);
}

/* ======================================================
   Language logic
   ====================================================== */
function setLanguage(lang, evt = null) {
    currentLanguage = lang;
    document.body.setAttribute('data-lang', lang);

    const buttonPreset = config.stylePresets?.button || {
        primary: 'bg-gradient-to-br from-blue-500 to-purple-600 text-white',
        secondary: 'bg-gray-100 text-gray-500 hover:bg-gray-200'
    };

    // イベントが無ければ、対応する言語ボタンを自動選択
    let targetBtn = evt?.target;
    if (!targetBtn) {
        document.querySelectorAll('.lang-btn').forEach(btn => {
            if (
                (lang === 'ja' && btn.textContent.includes('日本語')) ||
                (lang === 'en' && btn.textContent.includes('English'))
            ) {
                targetBtn = btn;
            }
        });
    }

    // ボタン状態リセット
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.className = `lang-btn ${buttonPreset.secondary}`;
    });

    // 対象ボタンをアクティブに
    if (targetBtn) {
        targetBtn.className = `lang-btn active ${buttonPreset.primary}`;
    }

    // 保存
    localStorage.setItem('preferredLanguage', lang);
}

/** 言語設定読み込み */
function loadLanguagePreference() {
    const saved = localStorage.getItem('preferredLanguage') || config.defaultLanguage || 'ja';
    setLanguage(saved, null);
}

/**
 * テキスト取得ヘルパー
 */
function getText(lang, path) {
    return getTextSafe(lang, path);
}

/** Init */
document.addEventListener('DOMContentLoaded', loadApplicationData);
