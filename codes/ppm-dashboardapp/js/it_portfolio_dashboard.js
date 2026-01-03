/**
 * IT Portfolio Management Dashboard - Multiple JSON Data Loading (Config対応版)
 * 3つのJSONファイルから動的にUIを生成
 */

let currentLanguage = window.APP_CONFIG?.defaultLanguage || 'ja';
let dashboardData = {
    metrics: null,
    budgetAllocation: null,
    strategicInvestment: null,
    projects: null,
    risks: null,
    milestones: null,
    resourceAllocation: null
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
async function loadDashboardData() {
    try {
        // 1. YAML設定を読み込み
        if (window.loadConfig) {
            await window.loadConfig();
        }
        
        // 2. 3つのJSONファイルを並列で読み込み
        const portfolioPath = (window.getDataPath && window.getDataPath('it_portfolio')) || '../data/it_portfolio.json';
        const projectsPath = (window.getDataPath && window.getDataPath('primary_projects')) || '../data/primary_projects.json';
        const resourcePath = (window.getDataPath && window.getDataPath('resource_allocation')) || '../data/resource_allocation.json';
        
        const [portfolioData, projectsData, resourceData] = await Promise.all([
            fetchJSON(portfolioPath),
            fetchJSON(projectsPath),
            fetchJSON(resourcePath)
        ]);
        
        // 3. データをマージ
        dashboardData = {
            ...portfolioData,
            ...projectsData,
            ...resourceData
        };
        
        initializeDashboard();
    } catch (e) {
        console.error('データ読み込み失敗:', e);
        const errorMsg = (window.getText && window.getText(currentLanguage, 'itPortfolioDashboard.messages.loadError')) || 'データの読み込みに失敗しました';
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
    const container = document.querySelector('.max-w-\\[1600px\\]');
    if (container) {
        container.innerHTML = `
            <div class="bg-red-50 p-6 border border-red-200 rounded-lg text-center text-red-700 font-medium mt-8">
                ${msg}
            </div>
        `;
    }
}

/** 初期化 */
function initializeDashboard() {
    if (!dashboardData.metrics) return;

    renderMetrics();
    renderBudgetAllocation();
    renderStrategicInvestment();
    renderProjectsTable();
    renderResourceAllocation();
    renderRisks();
    renderMilestones();
    loadLanguagePreference();
}

/* ======================================================
   メトリクスカード(4つの統計カード)
   ====================================================== */
function renderMetrics() {
    const metricsContainer = document.querySelector('.grid.grid-cols-\\[repeat\\(auto-fit\\,minmax\\(250px\\,1fr\\)\\)\\]');
    if (!metricsContainer) return;

    const { metrics } = dashboardData;
    const t = (path) => {
        return {
            ja: getTextSafe('ja', `itPortfolioDashboard.${path}`),
            en: getTextSafe('en', `itPortfolioDashboard.${path}`)
        };
    };
    
    metricsContainer.innerHTML = `
        <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-blue-500">
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-ja">${t('metrics.totalProjects').ja}</div>
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-en">${t('metrics.totalProjects').en}</div>
            <div class="text-4xl font-bold text-gray-800 mb-1">${metrics.totalProjects.value}</div>
            <div class="text-xs text-gray-400 lang-ja">${t('metrics.inProgress').ja}${metrics.totalProjects.inProgress} | ${t('metrics.planned').ja}${metrics.totalProjects.planned}</div>
            <div class="text-xs text-gray-400 lang-en">${t('metrics.inProgress').en}${metrics.totalProjects.inProgress} | ${t('metrics.planned').en}${metrics.totalProjects.planned}</div>
        </div>
        
        <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-green-500">
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-ja">${t('metrics.totalInvestment').ja}</div>
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-en">${t('metrics.totalInvestment').en}</div>
            <div class="text-4xl font-bold text-gray-800 mb-1">${metrics.totalInvestment.value}</div>
            <div class="text-xs text-gray-400 lang-ja">${t('metrics.budgetUtilization').ja}${metrics.totalInvestment.budgetUtilization}</div>
            <div class="text-xs text-gray-400 lang-en">${t('metrics.budgetUtilization').en}${metrics.totalInvestment.budgetUtilization}</div>
        </div>
        
        <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-amber-500">
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-ja">${t('metrics.averageROI').ja}</div>
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-en">${t('metrics.averageROI').en}</div>
            <div class="text-4xl font-bold text-gray-800 mb-1">${metrics.averageROI.value}</div>
            <div class="text-xs text-gray-400 lang-ja">${t('metrics.target').ja}${metrics.averageROI.target}</div>
            <div class="text-xs text-gray-400 lang-en">${t('metrics.target').en}${metrics.averageROI.target}</div>
        </div>
        
        <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-red-500">
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-ja">${t('metrics.highRiskProjects').ja}</div>
            <div class="text-gray-500 text-xs mb-2 uppercase tracking-wide lang-en">${t('metrics.highRiskProjects').en}</div>
            <div class="text-4xl font-bold text-gray-800 mb-1">${metrics.highRiskProjects.value}</div>
            <div class="text-xs text-gray-400 lang-ja">${t('metrics.requiresAttention').ja}</div>
            <div class="text-xs text-gray-400 lang-en">${t('metrics.requiresAttention').en}</div>
        </div>
    `;
}

/* ======================================================
   予算配分 (Run/Grow/Transform)
   ====================================================== */
function renderBudgetAllocation() {
    const container = document.querySelector('.grid.grid-cols-2 .bg-white');
    if (!container) return;

    const { budgetAllocation } = dashboardData;
    const t = (path) => {
        return {
            ja: getTextSafe('ja', `itPortfolioDashboard.${path}`),
            en: getTextSafe('en', `itPortfolioDashboard.${path}`)
        };
    };
    
    const budgetHTML = `
        <h2 class="text-lg font-semibold text-gray-800 mb-5 pb-2.5 border-b-2 border-gray-200 lang-ja">${t('budget.title').ja}</h2>
        <h2 class="text-lg font-semibold text-gray-800 mb-5 pb-2.5 border-b-2 border-gray-200 lang-en">${t('budget.title').en}</h2>
        
        <div class="space-y-6">
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('budget.run').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('budget.run').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${budgetAllocation.run.percent}% (${budgetAllocation.run.amount})</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-blue-500 rounded-full" style="width: ${budgetAllocation.run.percent}%;"></div>
                </div>
            </div>
            
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('budget.grow').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('budget.grow').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${budgetAllocation.grow.percent}% (${budgetAllocation.grow.amount})</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-green-500 rounded-full" style="width: ${budgetAllocation.grow.percent}%;"></div>
                </div>
            </div>
            
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('budget.transform').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('budget.transform').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${budgetAllocation.transform.percent}% (${budgetAllocation.transform.amount})</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-amber-500 rounded-full" style="width: ${budgetAllocation.transform.percent}%;"></div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = budgetHTML;
}

/* ======================================================
   戦略目標別投資
   ====================================================== */
function renderStrategicInvestment() {
    const containers = document.querySelectorAll('.grid.grid-cols-2 .bg-white');
    if (containers.length < 2) return;

    const { strategicInvestment } = dashboardData;
    const t = (path) => {
        return {
            ja: getTextSafe('ja', `itPortfolioDashboard.${path}`),
            en: getTextSafe('en', `itPortfolioDashboard.${path}`)
        };
    };
    
    const investmentHTML = `
        <h2 class="text-lg font-semibold text-gray-800 mb-5 pb-2.5 border-b-2 border-gray-200 lang-ja">${t('strategic.title').ja}</h2>
        <h2 class="text-lg font-semibold text-gray-800 mb-5 pb-2.5 border-b-2 border-gray-200 lang-en">${t('strategic.title').en}</h2>
        
        <div class="space-y-4">
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('strategic.customerExperience').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('strategic.customerExperience').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${strategicInvestment.customerExperience}%</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-blue-500 rounded-full" style="width: ${strategicInvestment.customerExperience}%;"></div>
                </div>
            </div>
            
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('strategic.operationalEfficiency').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('strategic.operationalEfficiency').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${strategicInvestment.operationalEfficiency}%</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-green-500 rounded-full" style="width: ${strategicInvestment.operationalEfficiency}%;"></div>
                </div>
            </div>
            
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('strategic.newBusiness').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('strategic.newBusiness').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${strategicInvestment.newBusiness}%</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-amber-500 rounded-full" style="width: ${strategicInvestment.newBusiness}%;"></div>
                </div>
            </div>
            
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('strategic.security').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('strategic.security').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${strategicInvestment.security}%</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-red-500 rounded-full" style="width: ${strategicInvestment.security}%;"></div>
                </div>
            </div>
            
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="text-sm text-gray-700 lang-ja">${t('strategic.infrastructure').ja}</div>
                    <div class="text-sm text-gray-700 lang-en">${t('strategic.infrastructure').en}</div>
                    <div class="text-sm font-semibold text-gray-800">${strategicInvestment.infrastructure}%</div>
                </div>
                <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-gray-500 rounded-full" style="width: ${strategicInvestment.infrastructure}%;"></div>
                </div>
            </div>
        </div>
    `;
    
    containers[1].innerHTML = investmentHTML;
}

/* ======================================================
   主要プロジェクト一覧テーブル
   ====================================================== */
function renderProjectsTable() {
    const tbody = document.querySelector('#projectsTable tbody');
    if (!tbody) return;

    const statusConfig = config.dashboardStatusColors || config.projectStatusColors;

    tbody.innerHTML = dashboardData.projects.map(project => {
        const statusStyle = statusConfig[project.status] || { bg: 'bg-gray-100', text: 'text-gray-700' };
        const statusTextJA = getTextSafe('ja', `itPortfolioDashboard.projectTable.${project.status}`);
        const statusTextEN = getTextSafe('en', `itPortfolioDashboard.projectTable.${project.status}`);
        
        // プログレスバーの色を決定
        let progressColor = 'bg-green-500';
        if (project.status === 'delayed') {
            progressColor = 'bg-red-500';
        } else if (project.status === 'caution') {
            progressColor = 'bg-amber-500';
        }
        
        return `
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="py-3 px-2 border-b border-gray-100">
                    <div class="font-medium text-gray-800 lang-ja">${project.nameJA}</div>
                    <div class="font-medium text-gray-800 lang-en">${project.nameEN}</div>
                </td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${statusStyle.bg} ${statusStyle.text} lang-ja">${statusTextJA}</span>
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${statusStyle.bg} ${statusStyle.text} lang-en">${statusTextEN}</span>
                </td>
                <td class="py-3 px-2 border-b border-gray-100 text-sm text-gray-700">${project.budget}</td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <div class="flex items-center gap-2">
                        <span class="text-xs">${project.progress}%</span>
                        <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden max-w-[100px]">
                            <div class="h-full ${progressColor} rounded-full" style="width: ${project.progress}%;"></div>
                        </div>
                    </div>
                </td>
                <td class="py-3 px-2 border-b border-gray-100 text-sm text-gray-700">${project.goal}</td>
                <td class="py-3 px-2 border-b border-gray-100 text-sm font-semibold text-gray-800">${project.roiForecast}</td>
            </tr>
        `;
    }).join('');
}

/* ======================================================
   リソース配置状況
   ====================================================== */
function renderResourceAllocation() {
    const tbody = document.querySelector('#resourceTable tbody');
    if (!tbody) return;

    const statusConfig = config.resourceStatusColors || {};

    tbody.innerHTML = dashboardData.resourceAllocation.map(resource => {
        const currentStatus = statusConfig[resource.current] || { bg: 'bg-gray-100', text: 'text-gray-700' };
        const threeMonthsStatus = statusConfig[resource.threeMonths] || { bg: 'bg-gray-100', text: 'text-gray-700' };
        const endOfTermStatus = statusConfig[resource.endOfTerm] || { bg: 'bg-gray-100', text: 'text-gray-700' };
        
        const currentTextJA = getTextSafe('ja', `itPortfolioDashboard.resources.${resource.current}`);
        const currentTextEN = getTextSafe('en', `itPortfolioDashboard.resources.${resource.current}`);
        const threeMonthsTextJA = getTextSafe('ja', `itPortfolioDashboard.resources.${resource.threeMonths}`);
        const threeMonthsTextEN = getTextSafe('en', `itPortfolioDashboard.resources.${resource.threeMonths}`);
        const endOfTermTextJA = getTextSafe('ja', `itPortfolioDashboard.resources.${resource.endOfTerm}`);
        const endOfTermTextEN = getTextSafe('en', `itPortfolioDashboard.resources.${resource.endOfTerm}`);
        
        // 稼働率に応じた色を決定
        let utilizationColor = 'bg-green-500';
        if (resource.utilization >= 90) {
            utilizationColor = 'bg-red-500';
        } else if (resource.utilization >= 80) {
            utilizationColor = 'bg-amber-500';
        }
        
        const peopleTextJA = getTextSafe('ja', 'itPortfolioDashboard.resources.people');
        
        return `
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="py-3 px-2 border-b border-gray-100">
                    <span class="lang-ja">${resource.roleJA}</span>
                    <span class="lang-en">${resource.roleEN}</span>
                </td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <span class="lang-ja">${resource.available}${peopleTextJA}</span>
                    <span class="lang-en">${resource.available}</span>
                </td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <div class="flex items-center gap-2">
                        <span class="text-xs">${resource.utilization}%</span>
                        <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden max-w-[100px]">
                            <div class="h-full ${utilizationColor} rounded-full" style="width: ${resource.utilization}%;"></div>
                        </div>
                    </div>
                </td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${currentStatus.bg} ${currentStatus.text} lang-ja">${currentTextJA}</span>
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${currentStatus.bg} ${currentStatus.text} lang-en">${currentTextEN}</span>
                </td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${threeMonthsStatus.bg} ${threeMonthsStatus.text} lang-ja">${threeMonthsTextJA}</span>
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${threeMonthsStatus.bg} ${threeMonthsStatus.text} lang-en">${threeMonthsTextEN}</span>
                </td>
                <td class="py-3 px-2 border-b border-gray-100">
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${endOfTermStatus.bg} ${endOfTermStatus.text} lang-ja">${endOfTermTextJA}</span>
                    <span class="py-1 px-2.5 rounded-lg text-xs font-semibold ${endOfTermStatus.bg} ${endOfTermStatus.text} lang-en">${endOfTermTextEN}</span>
                </td>
            </tr>
        `;
    }).join('');
}

/* ======================================================
   主要リスク・課題
   ====================================================== */
function renderRisks() {
    const grids = document.querySelectorAll('.grid.grid-cols-2');
    if (grids.length < 2) return;
    
    const riskContainer = grids[1].querySelector('.bg-white ul');
    if (!riskContainer) return;

    const levelConfig = config.riskLevelColors;

    riskContainer.innerHTML = dashboardData.risks.map(risk => {
        const borderClass = levelConfig[risk.level] || 'border-gray-500';
        const levelTextJA = getTextSafe('ja', `itPortfolioDashboard.risks.${risk.level}`);
        const levelTextEN = getTextSafe('en', `itPortfolioDashboard.risks.${risk.level}`);
        
        return `
            <li class="p-4 rounded-lg border-l-4 ${borderClass} bg-gray-50">
                <div class="font-semibold text-sm text-gray-800 mb-1 lang-ja">【${levelTextJA}】${risk.titleJA}</div>
                <div class="font-semibold text-sm text-gray-800 mb-1 lang-en">[${levelTextEN}] ${risk.titleEN}</div>
                <div class="text-xs text-gray-600 lang-ja">${risk.descriptionJA}</div>
                <div class="text-xs text-gray-600 lang-en">${risk.descriptionEN}</div>
            </li>
        `;
    }).join('');
}

/* ======================================================
   今後の重要マイルストーン
   ====================================================== */
function renderMilestones() {
    const grids = document.querySelectorAll('.grid.grid-cols-2');
    if (grids.length < 2) return;
    
    const containers = grids[1].querySelectorAll('.bg-white');
    if (containers.length < 2) return;
    
    const milestoneContainer = containers[1].querySelector('ul');
    if (!milestoneContainer) return;

    const levelConfig = config.riskLevelColors;

    milestoneContainer.innerHTML = dashboardData.milestones.map(milestone => {
        const borderClass = levelConfig[milestone.level] || 'border-gray-500';
        const date = new Date(milestone.date);
        const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
        const dateStrEN = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        return `
            <li class="p-4 rounded-lg border-l-4 ${borderClass} bg-gray-50">
                <div class="font-semibold text-sm text-gray-800 mb-1 lang-ja">${dateStr}: ${milestone.titleJA}</div>
                <div class="font-semibold text-sm text-gray-800 mb-1 lang-en">${dateStrEN}: ${milestone.titleEN}</div>
                <div class="text-xs text-gray-600 lang-ja">${milestone.descriptionJA}</div>
                <div class="text-xs text-gray-600 lang-en">${milestone.descriptionEN}</div>
            </li>
        `;
    }).join('');
}

/* ======================================================
   言語切り替え
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
    
    // 設定を保存
    localStorage.setItem('preferredLanguage', lang);
}

/** 言語設定読み込み */
function loadLanguagePreference() {
    const saved = localStorage.getItem('preferredLanguage') || config.defaultLanguage || 'ja';
    setLanguage(saved, null);
}

/** Init */
document.addEventListener('DOMContentLoaded', loadDashboardData);
