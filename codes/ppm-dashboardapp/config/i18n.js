/**
 * 多言語対応ファイル (i18n - Internationalization)
 */

window.I18N = {
    ja: {
        // ========== Application Layer View ==========
        applicationLayerView: {
            header: {
                title: 'アプリケーション鳥瞰図',
                subtitle: '全社システムマップとプロジェクト関連図'
            },
            sidebar: {
                projectList: 'プロジェクト一覧',
                clearSelection: '🔄 選択解除'
            },
            main: {
                applicationList: 'アプリケーション一覧',
                defaultStatus: '通常状態',
                projectRelated: 'プロジェクト関連'
            },
            eol: {
                title: '🔔 EOL(サポート終了)ステータス:',
                critical: '危険 (1年以内)',
                warning: '警告 (1-2年)',
                safe: '安全 (2年以上)',
                unknown: '不明'
            },
            messages: {
                loadError: 'アプリケーションデータの読み込みに失敗しました。',
                noData: 'データがありません。'
            }
        },

        // ========== Project View ==========
        projectView: {
            header: {
                title: 'プロジェクト鳥瞰図',
                subtitle: '全社プロジェクトの概要と進捗状況'
            },
            sidebar: {
                departments: '部門一覧',
                loading: '読み込み中...',
                projects: 'プロジェクト',
                allDepartments: 'すべて'
            },
            main: {
                projectList: 'プロジェクト一覧',
                loading: '読み込み中...'
            },
            card: {
                phase: 'フェーズ',
                budget: '予算',
                progress: '進捗',
                duration: '期間:',
                goal: '目標:'
            },
            status: {
                onTrack: '順調',
                atRisk: '注意',
                delayed: '遅延',
                completed: '完了',
                planning: '計画中'
            },
            messages: {
                loadError: 'データの読み込みに失敗しました。ページを再読み込みしてください。',
                noData: 'データがありません。'
            }
        },

        // ========== IT Portfolio Dashboard ==========
        itPortfolioDashboard: {
            header: {
                title: 'ITポートフォリオ管理ダッシュボード',
                lastUpdated: '最終更新:',
                quarter: '第4四半期'
            },
            metrics: {
                totalProjects: '総プロジェクト数',
                inProgress: '進行中:',
                planned: '計画中:',
                totalInvestment: '総投資額',
                budgetUtilization: '予算執行率:',
                averageROI: '平均ROI',
                target: '目標:',
                highRiskProjects: '高リスクPJ',
                requiresAttention: '要注意プロジェクト'
            },
            budget: {
                title: '予算配分 (Run/Grow/Transform)',
                run: 'Run (維持・運用)',
                grow: 'Grow (改善・拡大)',
                transform: 'Transform (変革)'
            },
            strategic: {
                title: '戦略目標別投資',
                customerExperience: '顧客体験向上',
                operationalEfficiency: '業務効率化',
                newBusiness: '新規事業創出',
                security: 'セキュリティ強化',
                infrastructure: '基盤刷新'
            },
            projectTable: {
                title: '主要プロジェクト一覧',
                projectName: 'プロジェクト名',
                status: 'ステータス',
                budget: '予算',
                progress: '進捗率',
                strategicGoal: '戦略目標',
                roiForecast: 'ROI予測',
                onTrack: '順調',
                caution: '注意',
                delayed: '遅延'
            },
            goals: {
                customerExperience: '顧客体験向上',
                infrastructure: '基盤刷新',
                operationalEfficiency: '業務効率化',
                newBusiness: '新規事業創出',
                security: 'セキュリティ強化'
            },
            risks: {
                title: '主要リスク・課題',
                high: '高',
                medium: '中',
                low: '低'
            },
            milestones: {
                title: '今後の重要マイルストーン'
            },
            resources: {
                title: '人的リソース配置状況と稼働率',
                teamRole: 'チーム/役割',
                available: '配置可能人数',
                utilization: '稼働率',
                current: '当月',
                threeMonths: '3ヶ月',
                termEnd: '今期末',
                overload: '過負荷',
                high: '高稼働',
                optimal: '適正',
                available: '余裕あり',
                note: '※ステータス:「当月」は当月の状況、「3ヶ月」は当月を含む3ヶ月間の見込み、「今期末」は今期末までの見込みを示します。',
                people: '名'
            },
            messages: {
                loadError: 'ダッシュボードデータの読み込みに失敗しました。',
                noData: 'データがありません。'
            }
        },

        // ========== 共通 ==========
        common: {
            language: {
                ja: '日本語',
                en: 'English'
            }
        }
    },

    en: {
        // ========== Application Layer View ==========
        applicationLayerView: {
            header: {
                title: 'Application Layer Overview',
                subtitle: 'Enterprise System Map & Project Relations'
            },
            sidebar: {
                projectList: 'Project List',
                clearSelection: '🔄 Clear Selection'
            },
            main: {
                applicationList: 'Application List',
                defaultStatus: 'Default',
                projectRelated: 'Project Related'
            },
            eol: {
                title: '🔔 EOL (End of Life) Status:',
                critical: 'Critical (<1 year)',
                warning: 'Warning (1-2 years)',
                safe: 'Safe (>2 years)',
                unknown: 'Unknown'
            },
            messages: {
                loadError: 'Failed to load application data.',
                noData: 'No data available.'
            }
        },

        // ========== Project View ==========
        projectView: {
            header: {
                title: 'Project Overview',
                subtitle: 'Overview and progress of company-wide projects'
            },
            sidebar: {
                departments: 'Departments',
                loading: 'Loading...',
                projects: 'Projects',
                allDepartments: 'All'
            },
            main: {
                projectList: 'Project List',
                loading: 'Loading...'
            },
            card: {
                phase: 'Phase',
                budget: 'Budget',
                progress: 'Progress',
                duration: 'Duration:',
                goal: 'Goal:'
            },
            status: {
                onTrack: 'On Track',
                atRisk: 'At Risk',
                delayed: 'Delayed',
                completed: 'Completed',
                planning: 'Planning'
            },
            messages: {
                loadError: 'Failed to load data. Please reload the page.',
                noData: 'No data available.'
            }
        },

        // ========== IT Portfolio Dashboard ==========
        itPortfolioDashboard: {
            header: {
                title: 'IT Portfolio Management Dashboard',
                lastUpdated: 'Last Updated:',
                quarter: 'Q4'
            },
            metrics: {
                totalProjects: 'Total Projects',
                inProgress: 'In Progress:',
                planned: 'Planned:',
                totalInvestment: 'Total Investment',
                budgetUtilization: 'Budget Utilization:',
                averageROI: 'Average ROI',
                target: 'Target:',
                highRiskProjects: 'High Risk Projects',
                requiresAttention: 'Requires Attention'
            },
            budget: {
                title: 'Budget Allocation (Run/Grow/Transform)',
                run: 'Run (Maintenance & Operations)',
                grow: 'Grow (Improvement & Expansion)',
                transform: 'Transform (Transformation)'
            },
            strategic: {
                title: 'Investment by Strategic Goal',
                customerExperience: 'Customer Experience Enhancement',
                operationalEfficiency: 'Operational Efficiency',
                newBusiness: 'New Business Development',
                security: 'Security Enhancement',
                infrastructure: 'Infrastructure Renewal'
            },
            projectTable: {
                title: 'Major Projects List',
                projectName: 'Project Name',
                status: 'Status',
                budget: 'Budget',
                progress: 'Progress',
                strategicGoal: 'Strategic Goal',
                roiForecast: 'ROI Forecast',
                onTrack: 'On Track',
                caution: 'Caution',
                delayed: 'Delayed'
            },
            goals: {
                customerExperience: 'Customer Experience',
                infrastructure: 'Infrastructure',
                operationalEfficiency: 'Efficiency',
                newBusiness: 'New Business',
                security: 'Security'
            },
            risks: {
                title: 'Major Risks & Issues',
                high: 'High',
                medium: 'Medium',
                low: 'Low'
            },
            milestones: {
                title: 'Upcoming Key Milestones'
            },
            resources: {
                title: 'Human Resource Allocation and Utilization',
                teamRole: 'Team/Role',
                available: 'Available',
                utilization: 'Utilization',
                current: 'Current',
                threeMonths: '3 Months',
                termEnd: 'Term End',
                overload: 'Overloaded',
                high: 'High Load',
                optimal: 'Optimal',
                available: 'Available',
                note: '※Status: "Current" shows current month status, "3 Months" shows forecast including current month, "Term End" shows forecast until end of term.',
                people: ''
            },
            messages: {
                loadError: 'Failed to load dashboard data.',
                noData: 'No data available.'
            }
        },

        // ========== 共通 ==========
        common: {
            language: {
                ja: '日本語',
                en: 'English'
            }
        }
    }
};

/**
 * テキスト取得ヘルパー関数
 * @param {string} lang - 言語コード ('ja' or 'en')
 * @param {string} path - テキストパス (例: 'applicationLayerView.header.title')
 * @returns {string} - 対応するテキスト
 */
window.getText = function(lang, path) {
    const keys = path.split('.');
    let result = window.I18N[lang];
    
    for (const key of keys) {
        if (result && result[key] !== undefined) {
            result = result[key];
        } else {
            console.warn(`Translation not found: ${lang}.${path}`);
            return path;
        }
    }
    
    return result;
};