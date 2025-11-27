// tailwind.config = {
//     theme: {
//         extend: {
//             colors: {
//                 // 企業ブランドカラー
//                 "kkc-orange": "#FF7600",
//                 "kkc-orange-light": "#FF8F33",
//                 "kkc-orange-dark": "#CC5F00",
                
//                 // 言語切替時のグラデーションカラー
//                 "gradient-start": "#667eea",
//                 "gradient-end": "#764ba2"
//             }
//         } 
//     }
// };

// アプリケーション設定
window.APP_CONFIG = {
    // レイアウト設定
    layout: {
        maxWidth: '1600px',
        sidebarWidth: '300px',
        cardMinWidth: '200px',
        gridGap: '20px'
    },

    // EOLステータスの色定義
    eolColors: {
        critical: { bg: 'bg-red-500', text: 'text-red-700', hex: '#ef4444' },
        warning: { bg: 'bg-amber-500', text: 'text-amber-700', hex: '#f59e0b' },
        safe: { bg: 'bg-green-500', text: 'text-green-700', hex: '#10b981' },
        unknown: { bg: 'bg-gray-400', text: 'text-gray-700', hex: '#9ca3af' }
    },

    // EOLステータスの閾値（日数）
    eolThresholds: {
        critical: 365,  // 1年以内
        warning: 730,   // 2年以内
        safe: Infinity  // それ以上
    },

    // カテゴリー別の色
    categoryColors: {
        default: 'bg-blue-100 text-blue-700',
        primary: 'bg-purple-100 text-purple-700',
        secondary: 'bg-green-100 text-green-700'
    },

    // プロジェクトステータスの色
    projectStatusColors: {
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
    },

    // ダッシュボードステータスの色
    dashboardStatusColors: {
        onTrack: {
            bg: 'bg-green-100',
            text: 'text-green-800',
            bar: 'bg-green-500'
        },
        caution: {
            bg: 'bg-amber-100',
            text: 'text-amber-800',
            bar: 'bg-amber-500'
        },
        delayed: {
            bg: 'bg-red-100',
            text: 'text-red-800',
            bar: 'bg-red-500'
        }
    },

    // リソースステータスの色
    resourceStatusColors: {
        overload: {
            bg: 'bg-red-100',
            text: 'text-red-800',
            bar: 'bg-red-500'
        },
        high: {
            bg: 'bg-amber-100',
            text: 'text-amber-800',
            bar: 'bg-amber-500'
        },
        optimal: {
            bg: 'bg-green-100',
            text: 'text-green-800',
            bar: 'bg-green-500'
        },
        available: {
            bg: 'bg-green-100',
            text: 'text-green-800',
            bar: 'bg-green-500'
        }
    },

    // リスクレベルの色
    riskLevelColors: {
        high: 'border-red-500',
        medium: 'border-amber-500',
        low: 'border-green-500'
    },

    // アニメーション設定
    animations: {
        transitionDuration: '300ms',
        hoverTranslateY: '-4px',
        hoverTranslateX: '4px',
        pulseScale: { start: 1, end: 1.02 },
        pulseDuration: '2s'
    },

    // スタイルクラスのプリセット
    stylePresets: {
        card: {
            base: 'relative bg-gray-50 p-5 rounded-xl border-2 border-gray-200 transition-all duration-300',
            hover: 'hover:shadow-lg hover:-translate-y-1',
            highlighted: 'bg-gradient-to-br from-amber-400/15 to-amber-500/15 border-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.5)]',
            pulse: 'animate-pulse-subtle'
        },
        projectCard: {
            base: 'bg-white p-5 rounded-xl shadow-sm border-2 border-gray-200 transition-all duration-300',
            hover: 'hover:shadow-md hover:scale-[1.02]',
            highlighted: 'highlighted highlight-pulse'
        },
        button: {
            primary: 'px-4 py-2 bg-gradient-to-br from-gradient-start to-gradient-end text-white rounded-full font-semibold text-xs transition-all duration-300',
            secondary: 'px-4 py-2 bg-gray-100 text-gray-500 rounded-full font-semibold text-xs transition-all duration-300 hover:bg-gray-200',
            clear: 'mt-5 w-full py-2.5 bg-gray-100 text-gray-700 border-0 rounded-lg cursor-pointer text-sm font-medium transition-all duration-300 hover:bg-gray-200'
        },
        projectItem: {
            base: 'project-item p-3 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-l-transparent bg-gray-50',
            hover: 'hover:bg-gray-100 hover:border-l-gradient-start hover:translate-x-1',
            active: 'active bg-gradient-to-br from-[rgba(102,126,234,0.1)] to-[rgba(118,75,162,0.1)] font-semibold'
        },
        departmentItem: {
            base: 'department-item p-3 px-4 mb-2 rounded-lg cursor-pointer transition-all duration-300 border-l-[3px] border-transparent bg-gray-50',
            hover: 'hover:bg-gray-100 hover:border-l-purple-500 hover:translate-x-1',
            active: 'active bg-gradient-to-br from-purple-500/10 to-purple-700/10 border-l-purple-500 font-semibold'
        }
    },

    // デフォルト言語設定
    defaultLanguage: 'ja',

    // グリッド・レスポンシブ設定
    responsive: {
        breakpoints: {
            sm: '640px',
            md: '768px',
            lg: '1024px',
            xl: '1280px'
        },
        gridColumns: {
            default: 'repeat(auto-fill,minmax(200px,1fr))',
            tablet: 'repeat(auto-fill,minmax(180px,1fr))',
            mobile: 'repeat(auto-fill,minmax(150px,1fr))'
        }
    }
};

/**
 * YAML設定を読み込む関数
 * YAMLパーサーライブラリ（js-yaml）を使用
 */
window.loadConfig = async function() {
    try {
        const response = await fetch('../config/config.yaml');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const yamlText = await response.text();
        
        // YAMLをパース（js-yamlライブラリが必要）
        if (typeof jsyaml !== 'undefined') {
            const yamlData = jsyaml.load(yamlText);
            window.APP_CONFIG.yaml = yamlData;
            
            // YAML設定でconfigを上書き
            if (yamlData.app?.default_language) {
                window.APP_CONFIG.defaultLanguage = yamlData.app.default_language;
            }
            if (yamlData.eol?.thresholds) {
                window.APP_CONFIG.eolThresholds = yamlData.eol.thresholds;
            }
            if (yamlData.eol?.colors) {
                // 16進数カラーコードをTailwindクラスに変換する処理は省略
                // 必要に応じてカスタマイズ可能
            }
            
            console.log('✅ YAML設定を読み込みました', yamlData);
            return yamlData;
        } else {
            console.warn('⚠️ js-yamlライブラリが読み込まれていません。デフォルト設定を使用します。');
            return null;
        }
    } catch (error) {
        console.error('❌ YAML読み込みエラー:', error);
        console.log('デフォルト設定を使用します。');
        return null;
    }
};

/**
 * データパスを取得する関数
 * @param {string} key - データソースのキー
 * @returns {string} - データファイルのパス
 */
window.getDataPath = function(key) {
    if (window.APP_CONFIG.yaml?.data_sources?.[key]) {
        return window.APP_CONFIG.yaml.data_sources[key];
    }
    // フォールバック
    return `../data/${key}.json`;
};