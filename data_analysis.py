import os
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = r"data\beer-dataset-master\beer-database"

def load_all_beer_data(data_dir):
    all_beers = []
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    print(f"正在加载 {len(json_files)} JSON 文件...")

    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_beers.extend(data.get('data', []))
    
    print(f"成功加载 {len(all_beers)} 条啤酒数据")
    return all_beers

def safe_float(value, default=None):
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def extract_beers_to_df(all_beers):
    records = []
    for beer in all_beers:
        record = {
            'id': beer.get('id'),
            'name': beer.get('name'),
            'abv': safe_float(beer.get('abv')),
            'ibu': safe_float(beer.get('ibu')),
            'is_organic': beer.get('isOrganic'),
            'is_retired': beer.get('isRetired'),
            'status': beer.get('status'),
            'style_name': beer.get('style', {}).get('name'),
            'style_short_name': beer.get('style', {}).get('shortName'),
            'category_name': beer.get('style', {}).get('category', {}).get('name'),
            'available_name': beer.get('available', {}).get('name'),
            'srm_id': beer.get('srm', {}).get('id'),
            'srm_name': beer.get('srm', {}).get('name'),
            'create_year': beer.get('createDate', '')[:4] if beer.get('createDate') else None
        }
        records.append(record)
    
    return pd.DataFrame(records)

def print_basic_stats(df):
    print("\n" + "="*60)
    print("数据基础统计信息")
    print("="*60)
    
    print(f"\n总数据量: {len(df)}")
    print(f"唯一啤酒风格数: {df['id'].nunique()}")
    print(f"缺失ABV数据的比例: {df['abv'].isna().mean()*100:.2f}%")
    print(f"缺失IBU数据的比例: {df['ibu'].isna().mean()*100:.2f}%")
    
    print(f"\nABV 统计:")
    print(f"  均值: {df['abv'].mean():.2f}%")
    print(f"  中位数: {df['abv'].median():.2f}%")
    print(f"  最小值: {df['abv'].min():.2f}%")
    print(f"  最大值: {df['abv'].max():.2f}%")
    
    print(f"\nIBU 统计:")
    print(f"  均值: {df['ibu'].mean():.2f}")
    print(f"  中位数: {df['ibu'].median():.2f}")
    print(f"  最小值: {df['ibu'].min():.2f}")
    print(f"  最大值: {df['ibu'].max():.2f}")

def plot_abv_distribution(df):
    plt.figure(figsize=(12, 6))
    abv_data = df['abv'].dropna()
    ax = sns.histplot(abv_data, bins=50, kde=True, color='#E97451')
    plt.title('啤酒酒精含量(ABV)分布', fontsize=14, fontweight='bold')
    plt.xlabel('酒精含量 (%)', fontsize=12)
    plt.ylabel('啤酒数量', fontsize=12)
    plt.axvline(abv_data.mean(), color='red', linestyle='--', linewidth=2, label=f'均值: {abv_data.mean():.2f}%')
    plt.axvline(abv_data.median(), color='green', linestyle=':', linewidth=2, label=f'中位数: {abv_data.median():.2f}%')
    plt.legend()
    plt.xlim(0, 20)
    plt.tight_layout()
    plt.savefig('plots/abv_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/abv_distribution.png")

def plot_ibu_distribution(df):
    plt.figure(figsize=(12, 6))
    ibu_data = df['ibu'].dropna()
    ax = sns.histplot(ibu_data, bins=50, kde=True, color='#5D4E37')
    plt.title('啤酒苦度值(IBU)分布', fontsize=14, fontweight='bold')
    plt.xlabel('苦度值 (IBU)', fontsize=12)
    plt.ylabel('啤酒数量', fontsize=12)
    plt.axvline(ibu_data.mean(), color='red', linestyle='--', linewidth=2, label=f'均值: {ibu_data.mean():.2f}')
    plt.axvline(ibu_data.median(), color='green', linestyle=':', linewidth=2, label=f'中位数: {ibu_data.median():.2f}')
    plt.legend()
    plt.xlim(0, 150)
    plt.tight_layout()
    plt.savefig('plots/ibu_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/ibu_distribution.png")

def plot_top_styles(df, top_n=15):
    plt.figure(figsize=(14, 8))
    style_counts = df['style_name'].dropna().value_counts().head(top_n)
    
    ax = sns.barplot(x=style_counts.values, y=style_counts.index, palette='viridis', orient='h')
    plt.title(f'Top {top_n} 啤酒风格分布', fontsize=14, fontweight='bold')
    plt.xlabel('啤酒数量', fontsize=12)
    plt.ylabel('啤酒风格', fontsize=12)
    
    for i, (_, count) in enumerate(style_counts.items()):
        ax.text(count, i, f' {count}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/top_styles.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/top_styles.png")

def plot_top_categories(df, top_n=10):
    plt.figure(figsize=(14, 8))
    category_counts = df['category_name'].dropna().value_counts().head(top_n)
    
    ax = sns.barplot(x=category_counts.values, y=category_counts.index, palette='magma', orient='h')
    plt.title(f'Top {top_n} 啤酒类别分布', fontsize=14, fontweight='bold')
    plt.xlabel('啤酒数量', fontsize=12)
    plt.ylabel('啤酒类别', fontsize=12)
    
    for i, (_, count) in enumerate(category_counts.items()):
        ax.text(count, i, f' {count}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/top_categories.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/top_categories.png")

def plot_organic_distribution(df):
    plt.figure(figsize=(10, 6))
    organic_counts = df['is_organic'].value_counts()
    colors = ['#8B4513', '#90EE90']
    labels = ['非有机', '有机']
    counts = [organic_counts.get('N', 0), organic_counts.get('Y', 0)]
    
    plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 12})
    plt.title('有机 vs 非有机啤酒比例', fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('plots/organic_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/organic_distribution.png")

def plot_retired_distribution(df):
    plt.figure(figsize=(10, 6))
    retired_counts = df['is_retired'].value_counts()
    colors = ['#2E8B57', '#FF6B6B']
    labels = ['在售', '已停产']
    counts = [retired_counts.get('N', 0), retired_counts.get('Y', 0)]
    
    plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 12})
    plt.title('在售 vs 已停产啤酒比例', fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('plots/retired_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/retired_distribution.png")

def plot_availability(df):
    plt.figure(figsize=(12, 6))
    avail_counts = df['available_name'].dropna().value_counts()
    
    ax = sns.barplot(x=avail_counts.values, y=avail_counts.index, palette='coolwarm', orient='h')
    plt.title('啤酒供应方式分布', fontsize=14, fontweight='bold')
    plt.xlabel('啤酒数量', fontsize=12)
    plt.ylabel('供应方式', fontsize=12)
    
    for i, (_, count) in enumerate(avail_counts.items()):
        ax.text(count, i, f' {count}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/availability.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/availability.png")

def plot_abv_ibu_scatter(df):
    plt.figure(figsize=(12, 8))
    valid_data = df.dropna(subset=['abv', 'ibu'])
    
    ax = sns.scatterplot(data=valid_data, x='abv', y='ibu', alpha=0.3, color='#CD853F', s=20)
    plt.title('ABV vs IBU 关系散点图', fontsize=14, fontweight='bold')
    plt.xlabel('酒精含量 (%)', fontsize=12)
    plt.ylabel('苦度值 (IBU)', fontsize=12)
    plt.xlim(0, 20)
    plt.ylim(0, 150)
    plt.tight_layout()
    plt.savefig('plots/abv_ibu_scatter.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/abv_ibu_scatter.png")

def plot_status_distribution(df):
    plt.figure(figsize=(12, 6))
    status_counts = df['status'].dropna().value_counts()
    
    ax = sns.barplot(x=status_counts.values, y=status_counts.index, palette='Set2', orient='h')
    plt.title('啤酒状态分布', fontsize=14, fontweight='bold')
    plt.xlabel('啤酒数量', fontsize=12)
    plt.ylabel('状态', fontsize=12)
    
    for i, (_, count) in enumerate(status_counts.items()):
        ax.text(count, i, f' {count}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/status_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/status_distribution.png")

def plot_year_distribution(df):
    plt.figure(figsize=(12, 6))
    year_counts = df['create_year'].dropna().value_counts().sort_index()
    
    ax = sns.barplot(x=year_counts.index, y=year_counts.values, palette='YlOrBr')
    plt.title('按年份统计啤酒数量', fontsize=14, fontweight='bold')
    plt.xlabel('年份', fontsize=12)
    plt.ylabel('啤酒数量', fontsize=12)
    plt.xticks(rotation=45)
    
    for i, (_, count) in enumerate(year_counts.items()):
        ax.text(i, count, str(count), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/year_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/year_distribution.png")

def plot_srm_distribution(df):
    plt.figure(figsize=(14, 7))
    srm_counts = df['srm_name'].dropna().value_counts().head(20)
    
    ax = sns.barplot(x=srm_counts.values, y=srm_counts.index, palette='YlOrRd', orient='h')
    plt.title('Top 20 SRM 颜色分布', fontsize=14, fontweight='bold')
    plt.xlabel('啤酒数量', fontsize=12)
    plt.ylabel('SRM 颜色', fontsize=12)
    
    for i, (_, count) in enumerate(srm_counts.items()):
        ax.text(count, i, f' {count}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('plots/srm_distribution.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/srm_distribution.png")

def plot_abv_by_category(df, top_n=10):
    top_categories = df['category_name'].value_counts().head(top_n).index
    filtered_df = df[df['category_name'].isin(top_categories)]
    
    plt.figure(figsize=(14, 8))
    ax = sns.boxplot(data=filtered_df, x='abv', y='category_name', palette='Set3')
    plt.title(f'Top {top_n} 啤酒类别 ABV 分布箱线图', fontsize=14, fontweight='bold')
    plt.xlabel('酒精含量 (%)', fontsize=12)
    plt.ylabel('啤酒类别', fontsize=12)
    plt.tight_layout()
    plt.savefig('plots/abv_by_category.png', dpi=300, bbox_inches='tight')
    print("已保存: plots/abv_by_category.png")

def main():
    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    all_beers = load_all_beer_data(DATA_DIR)
    df = extract_beers_to_df(all_beers)
    
    print_basic_stats(df)
    
    print("\n" + "="*60)
    print("开始生成图表...")
    print("="*60)
    
    plot_abv_distribution(df)
    plot_ibu_distribution(df)
    plot_top_styles(df)
    plot_top_categories(df)
    plot_organic_distribution(df)
    plot_retired_distribution(df)
    plot_availability(df)
    plot_abv_ibu_scatter(df)
    plot_status_distribution(df)
    plot_year_distribution(df)
    plot_srm_distribution(df)
    plot_abv_by_category(df)
    
    print("\n" + "="*60)
    print("所有图表已保存到 plots/ 目录下")
    print("="*60)

if __name__ == "__main__":
    main()
