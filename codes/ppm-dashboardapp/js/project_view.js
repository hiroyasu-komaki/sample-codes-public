/**
 * プロジェクト鳥瞰図 - データローダー (Config対応版)
 * Project Overview - Data Loader
 * departments.json と project_list.json を使用
 */

let currentLanguage = window.APP_CONFIG?.defaultLanguage || 'ja';
let projectData = {
    departments: null,
    projects: null
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

/**
 * 複数のJSONファイルをロード
 */
async function loadProjectData() {
    try {
        // 1. YAML設定を読み込み
        if (window.loadConfig) {
            await window.loadConfig();
        }
        
        // 2. データパスを取得
        const departmentsPath = (window.getDataPath && window.getDataPath('departments')) || '../data/departments.json';
        const projectsPath = (window.getDataPath && window.getDataPath('project_list')) || '../data/project_list.json';
        
        // 3. 2つのJSONファイルを並列で読み込み
        const [departmentsData, projectsListData] = await Promise.all([
            fetchJSON(departmentsPath),
            fetchJSON(projectsPath)
        ]);
        
        // 4. データをマージ
        projectData = {
            departments: departmentsData.departments,
            projects: projectsListData.projects
        };
        
        initializeApp();
    } catch (error) {
        console.error('データの読み込みに失敗しました:', error);
        const errorMsg = (window.getText && window.getText(currentLanguage, 'projectView.messages.loadError')) 
            || 'データの読み込みに失敗しました。ページを再読み込みしてください。';
        showError(errorMsg);
    }
}

/** JSONファイルをフェッチする共通関数 */
async function fetchJSON(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status} for ${url}`);
    return await response.json();
}

/**
 * エラーメッセージを表示
 */
function showError(message) {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <svg class="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-red-800 font-medium">${message}</p>
            </div>
        `;
    }
}

/**
 * アプリケーションを初期化
 */
function initializeApp() {
    if (!projectData.departments || !projectData.projects) return;
    
    renderDepartments();
    renderProjects();
    loadLanguagePreference();
}

/**
 * 部門リストをレンダリング
 */
function renderDepartments() {
    const departmentList = document.querySelector('aside ul');
    if (!departmentList) return;
    
    // 既存のリストをクリア
    departmentList.innerHTML = '';
    
    // 「すべて」を追加
    const allDept = projectData.departments.find(d => d.id === 'all');
    if (allDept) {
        departmentList.appendChild(createAllDepartmentItem(allDept));
    }
    
    // 各部門を追加
    projectData.departments.forEach(dept => {
        if (dept.id !== 'all') {
            departmentList.appendChild(createDepartmentItem(dept));
        }
    });
}

/**
 * 「すべて」部門アイテムを作成
 */
function createAllDepartmentItem(dept) {
    const preset = config.stylePresets?.departmentItem || {
        base: 'department-item p-3 px-4 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-transparent bg-gray-50',
        hover: 'hover:bg-gray-100 hover:border-l-purple-500 hover:translate-x-1',
        active: 'active bg-gradient-to-br from-purple-500/10 to-purple-700/10 border-l-purple-500 font-semibold'
    };
    
    const li = document.createElement('li');
    li.className = `${preset.base} ${preset.hover}`;
    li.onclick = () => clearSelection();
    
    const projectsTextJA = getTextSafe('ja', 'projectView.sidebar.projects');
    const projectsTextEN = getTextSafe('en', 'projectView.sidebar.projects');
    
    li.innerHTML = `
        <div class="text-sm text-gray-800 mb-1">
            <span class="lang-ja">${dept.nameJA}</span>
            <span class="lang-en">${dept.nameEN}</span>
        </div>
        <div class="text-xs text-gray-500">
            <span class="lang-ja">${dept.projectCount}${projectsTextJA}</span>
            <span class="lang-en">${dept.projectCount} ${projectsTextEN}</span>
        </div>
    `;
    
    return li;
}

/**
 * 部門アイテムを作成
 */
function createDepartmentItem(dept) {
    const preset = config.stylePresets?.departmentItem || {
        base: 'department-item p-3 px-4 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-transparent bg-gray-50',
        hover: 'hover:bg-gray-100 hover:border-l-purple-500 hover:translate-x-1',
        active: 'active bg-gradient-to-br from-purple-500/10 to-purple-700/10 border-l-purple-500 font-semibold'
    };
    
    const li = document.createElement('li');
    li.className = `${preset.base} ${preset.hover}`;
    li.setAttribute('data-department', dept.id);
    li.onclick = () => selectDepartment(dept.id);
    
    const projectsTextJA = getTextSafe('ja', 'projectView.sidebar.projects');
    const projectsTextEN = getTextSafe('en', 'projectView.sidebar.projects');
    
    li.innerHTML = `
        <div class="department-name text-sm text-gray-800 mb-1">
            <span class="lang-ja">${dept.nameJA}</span>
            <span class="lang-en">${dept.nameEN}</span>
        </div>
        <div class="department-count text-xs text-gray-500">
            <span class="lang-ja">${dept.projectCount}${projectsTextJA}</span>
            <span class="lang-en">${dept.projectCount} ${projectsTextEN}</span>
        </div>
    `;
    
    return li;
}

/**
 * プロジェクトカードをレンダリング
 */
function renderProjects() {
    const mainContent = document.querySelector('main');
    if (!mainContent) return;
    
    const projectListTextJA = getTextSafe('ja', 'projectView.main.projectList');
    const projectListTextEN = getTextSafe('en', 'projectView.main.projectList');
    
    mainContent.innerHTML = `
        <h2 class="text-xl font-bold text-gray-800 mb-5">
            <span class="lang-ja">${projectListTextJA}</span>
            <span class="lang-en">${projectListTextEN}</span>
            <span id="selectedDepartment" class="text-purple-600"></span>
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            ${projectData.projects.map(project => createProjectCard(project)).join('')}
        </div>
    `;
}

/**
 * プロジェクトカードを作成
 */
function createProjectCard(project) {
    const projectStatusColors = config.projectStatusColors || {
        'on-track': { 
            bg: 'bg-green-100', 
            text: 'text-green-800', 
            border: 'border-green-300', 
            progress: 'from-green-400 to-green-600' 
        },
        'at-risk': { 
            bg: 'bg-yellow-100', 
            text: 'text-yellow-800', 
            border: 'border-yellow-300', 
            progress: 'from-yellow-400 to-yellow-600' 
        },
        'delayed': { 
            bg: 'bg-red-100', 
            text: 'text-red-800', 
            border: 'border-red-300', 
            progress: 'from-red-400 to-red-600' 
        },
        'completed': { 
            bg: 'bg-blue-100', 
            text: 'text-blue-800', 
            border: 'border-blue-300', 
            progress: 'from-blue-400 to-blue-600' 
        },
        'planning': { 
            bg: 'bg-gray-100', 
            text: 'text-gray-800', 
            border: 'border-gray-300', 
            progress: 'from-gray-400 to-gray-600' 
        }
    };
    
    const colors = projectStatusColors[project.status] || projectStatusColors['planning'];
    
    const cardPreset = config.stylePresets?.projectCard || {
        base: 'bg-white p-5 rounded-xl shadow-sm border-2 border-gray-200 transition-all duration-300',
        hover: 'hover:shadow-md hover:scale-[1.02]',
        highlighted: 'highlighted highlight-pulse'
    };
    
    const phaseTextJA = getTextSafe('ja', 'projectView.card.phase');
    const phaseTextEN = getTextSafe('en', 'projectView.card.phase');
    const budgetTextJA = getTextSafe('ja', 'projectView.card.budget');
    const budgetTextEN = getTextSafe('en', 'projectView.card.budget');
    const progressTextJA = getTextSafe('ja', 'projectView.card.progress');
    const progressTextEN = getTextSafe('en', 'projectView.card.progress');
    const durationTextJA = getTextSafe('ja', 'projectView.card.duration');
    const durationTextEN = getTextSafe('en', 'projectView.card.duration');
    const goalTextJA = getTextSafe('ja', 'projectView.card.goal');
    const goalTextEN = getTextSafe('en', 'projectView.card.goal');
    
    return `
        <div class="${cardPreset.base} ${cardPreset.hover}" 
             data-department="${project.department}" 
             data-status="${project.status}">
            <div class="flex justify-between items-start mb-3">
                <h3 class="text-base font-bold text-gray-900 flex-1 mr-2">
                    <span class="lang-ja">${project.nameJA}</span>
                    <span class="lang-en">${project.nameEN}</span>
                </h3>
                <span class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${colors.bg} ${colors.text} ${colors.border} border">
                    <span class="lang-ja">${project.statusLabelJA}</span>
                    <span class="lang-en">${project.statusLabelEN}</span>
                </span>
            </div>
            
            <div class="mb-4 space-y-2 text-xs">
                <div class="flex justify-between">
                    <span class="text-gray-500">
                        <span class="lang-ja">${phaseTextJA}</span>
                        <span class="lang-en">${phaseTextEN}</span>
                    </span>
                    <span class="text-gray-800 font-medium">
                        <span class="lang-ja">${project.phaseLabelJA}</span>
                        <span class="lang-en">${project.phaseLabelEN}</span>
                    </span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-500">
                        <span class="lang-ja">${budgetTextJA}</span>
                        <span class="lang-en">${budgetTextEN}</span>
                    </span>
                    <span class="text-gray-800 font-medium">
                        <span class="lang-ja">${project.budgetJA}</span>
                        <span class="lang-en">${project.budgetEN}</span>
                    </span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-500">
                        <span class="lang-ja">${progressTextJA}</span>
                        <span class="lang-en">${progressTextEN}</span>
                    </span>
                    <span class="text-gray-800 font-medium">${project.progress}%</span>
                </div>
            </div>
            
            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-4">
                <div class="h-full bg-gradient-to-r ${colors.progress} transition-all duration-500" style="width: ${project.progress}%;"></div>
            </div>
            
            <div class="text-xs space-y-2 text-gray-600">
                <div>
                    <strong class="text-gray-800">
                        <span class="lang-ja">${durationTextJA}</span>
                        <span class="lang-en">${durationTextEN}</span>
                    </strong>
                    <span class="lang-ja">${project.durationJA}</span>
                    <span class="lang-en">${project.durationEN}</span>
                </div>
                <div>
                    <strong class="text-gray-800">
                        <span class="lang-ja">${goalTextJA}</span>
                        <span class="lang-en">${goalTextEN}</span>
                    </strong>
                    <span class="lang-ja">${project.goalJA}</span>
                    <span class="lang-en">${project.goalEN}</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * 言語を設定
 */
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
    
    // 設定を保存
    localStorage.setItem('preferredLanguage', lang);
}

/**
 * 部門を選択
 */
function selectDepartment(departmentId) {
    const cardPreset = config.stylePresets?.projectCard || {
        base: 'bg-white p-5 rounded-xl shadow-sm border-2 border-gray-200 transition-all duration-300',
        hover: 'hover:shadow-md hover:scale-[1.02]',
        highlighted: 'highlighted highlight-pulse'
    };
    
    const deptPreset = config.stylePresets?.departmentItem || {
        base: 'department-item p-3 px-4 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-transparent bg-gray-50',
        hover: 'hover:bg-gray-100 hover:border-l-purple-500 hover:translate-x-1',
        active: 'active bg-gradient-to-br from-purple-500/10 to-purple-700/10 border-l-purple-500 font-semibold'
    };
    
    // すべての部門選択をクリア
    document.querySelectorAll('.department-item').forEach(item => {
        item.className = `${deptPreset.base} ${deptPreset.hover}`;
    });
    
    // すべてのプロジェクトカードのハイライトをクリア
    document.querySelectorAll('[data-department][data-status]').forEach(card => {
        // department-itemではないカード（プロジェクトカード）のみ処理
        if (!card.classList.contains('department-item')) {
            card.className = `${cardPreset.base} ${cardPreset.hover}`;
            card.style.background = '';
            card.style.borderColor = '';
        }
    });
    
    if (departmentId) {
        // 選択された部門をハイライト
        const selectedDeptItem = document.querySelector(`.department-item[data-department="${departmentId}"]`);
        if (selectedDeptItem) {
            selectedDeptItem.className = `${deptPreset.base} ${deptPreset.hover} ${deptPreset.active}`;
        }
        
        // 関連プロジェクトをハイライト
        document.querySelectorAll('[data-department][data-status]').forEach(card => {
            const dept = card.getAttribute('data-department');
            if (dept === departmentId) {
                card.classList.add('highlighted', 'highlight-pulse');
                card.style.background = 'linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%)';
                card.style.borderColor = '#fbbf24';
            }
        });
        
        // タイトルを更新
        const dept = projectData.departments.find(d => d.id === departmentId);
        const selectedDeptSpan = document.getElementById('selectedDepartment');
        if (dept && selectedDeptSpan) {
            selectedDeptSpan.textContent = currentLanguage === 'ja' 
                ? ` - ${dept.nameJA}` 
                : ` - ${dept.nameEN}`;
        }
    } else {
        const selectedDeptSpan = document.getElementById('selectedDepartment');
        if (selectedDeptSpan) {
            selectedDeptSpan.textContent = '';
        }
    }
}

/**
 * 選択をクリア
 */
function clearSelection() {
    selectDepartment(null);
}

/**
 * 言語設定を読み込み
 */
function loadLanguagePreference() {
    const saved = localStorage.getItem('preferredLanguage') || config.defaultLanguage || 'ja';
    setLanguage(saved, null);
}

// ページ読み込み時にデータをフェッチ
document.addEventListener('DOMContentLoaded', loadProjectData);
