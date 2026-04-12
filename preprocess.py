#!/usr/bin/env python3
"""
城市共振：时空噪声色谱 - 数据预处理脚本 v2
支持真实 CSV 数据，自动从 domainId_txt 映射到 18 类噪声
"""

import pandas as pd
import numpy as np
import json
import argparse
import random
from datetime import datetime

# 18类分类定义 (矿物色谱 + 重墨风格)
CATEGORIES = [
    {"id": 0, "name": "基础施工", "color": "#2d5a5a", "penetration": 5},
    {"id": 1, "name": "室内装修", "color": "#235555", "penetration": 3},
    {"id": 2, "name": "拆除工程", "color": "#3d5a5a", "penetration": 5},
    {"id": 3, "name": "工厂运行", "color": "#0a0a0a", "penetration": 5},
    {"id": 4, "name": "非法排污", "color": "#1a1a1a", "penetration": 5},
    {"id": 5, "name": "中央空调/风机", "color": "#2a2a2a", "penetration": 4},
    {"id": 6, "name": "车辆鸣笛", "color": "#5a5a6a", "penetration": 4},
    {"id": 7, "name": "重型卡车", "color": "#4a4a5a", "penetration": 5},
    {"id": 8, "name": "刹车尖鸣", "color": "#6a6a7a", "penetration": 4},
    {"id": 9, "name": "广场舞", "color": "#8b3a3a", "penetration": 3},
    {"id": 10, "name": "商业扩音", "color": "#9b4a4a", "penetration": 3},
    {"id": 11, "name": "露天夜市", "color": "#ab5a5a", "penetration": 3},
    {"id": 12, "name": "宠物犬吠", "color": "#8b6b4a", "penetration": 2},
    {"id": 13, "name": "邻里纠纷", "color": "#7b5b3a", "penetration": 2},
    {"id": 14, "name": "空调滴水", "color": "#6b4b2a", "penetration": 2},
    {"id": 15, "name": "救护车/警笛", "color": "#5a4a6a", "penetration": 4},
    {"id": 16, "name": "轨道交通", "color": "#4a3a5a", "penetration": 4},
    {"id": 17, "name": "垃圾清运", "color": "#6a5a7a", "penetration": 3},
]

# domainId_txt → category 映射
# 从真实数据中的 domainId_txt 映射到 18 类
DOMAIN_TO_CATEGORY = {
    # 工地噪音 → 施工类
    '工地噪音': (0, 1),  # 随机分配 0-1
    '建设管理': (0, 1),
    '房屋建设规划问题': (2,),
    
    # 工业噪声问题 → 工业类
    '工业噪声问题': (3, 4),
    '安全生产': (3, 5),
    
    # 交通管理 → 交通类
    '交通管理': (6, 7, 8),
    
    # 商业噪音问题 → 社会类
    '商业噪音问题': (9, 10, 11),
    '油烟污染': (10, 11),
    
    # 生活噪声问题 → 生活类
    '生活噪声问题': (12, 13, 14),
    '物业纠纷': (13,),
    
    # 公共类
    '城市市容管理': (15, 16, 17),  # 包含垃圾、环卫等
    '公共设施维护': (15, 17),
    '公园、绿化广场管理问题': (16, 17),
    '社会服务': (15, 16),
    '生活垃圾': (17,),
    '烟草执法管理': (10,),
    
    # 待处理
    '待审核': (12, 13, 14),
    '待分类案件': (12, 13, 14),
    '其他': (12, 13, 14),
    '问题反映': (12, 13, 14),
    '意见建议': (12, 13, 14),
    '点赞': (12, 13, 14),
    '困难求助': (12, 13, 14),
    '商品房买卖纠纷': (13,),
    '占道经营': (11,),
}


def calculate_time_weight(hour: int) -> float:
    """
    深夜加成逻辑
    22:00 - 05:59: 3.0x (深夜最强)
    18:00 - 21:59: 1.5x - 3.0x (黄昏渐变)
    其他时间: 1.0x (标准)
    """
    if 22 <= hour or hour <= 5:
        return 3.0
    elif 18 <= hour < 22:
        return 1.5 + (hour - 18) * 0.375
    else:
        return 1.0


def map_domain_to_category(domain: str, content: str = '') -> int:
    """根据 domainId_txt 映射到 category ID"""
    domain = str(domain).strip()
    
    if domain in DOMAIN_TO_CATEGORY:
        candidates = DOMAIN_TO_CATEGORY[domain]
    else:
        # 模糊匹配
        for key, cats in DOMAIN_TO_CATEGORY.items():
            if key in domain or domain in key:
                candidates = cats
                break
        else:
            candidates = (12, 13, 14)  # 默认生活类
    
    # 随机选择一个候选类别
    return random.choice(candidates)


def process_data(input_file: str, output_file: str = 'noise_data.json'):
    """处理武汉噪声投诉数据"""
    print(f"📖 读取数据: {input_file}")
    df = pd.read_csv(input_file)
    print(f"   总记录: {len(df)}")
    
    # 过滤有效坐标
    df = df[df['baidu_lng'].notna() & df['baidu_lat'].notna()]
    df = df[(df['baidu_lng'] > 100) & (df['baidu_lng'] < 130)]  # 湖北附近
    df = df[(df['baidu_lat'] > 28) & (df['baidu_lat'] < 35)]
    print(f"   有效坐标: {len(df)}")
    
    results = []
    skipped = 0
    
    for idx, row in df.iterrows():
        try:
            # 坐标
            lon = float(row['baidu_lng'])
            lat = float(row['baidu_lat'])
            
            # 时间
            try:
                dt = pd.to_datetime(row['dateline_txt'])
                timestamp = int(dt.timestamp() * 1000)
                hour = dt.hour
            except:
                skipped += 1
                continue
            
            # 类别
            domain = row.get('domainId_txt', '其他')
            category_id = map_domain_to_category(domain, str(row.get('content', '')))
            category = CATEGORIES[category_id]
            
            # 时间权重 (深夜加成)
            time_weight = calculate_time_weight(hour)
            
            # 视觉权重
            weight = category['penetration'] * time_weight
            
            results.append({
                'lon': round(lon, 6),
                'lat': round(lat, 6),
                'timestamp': timestamp,
                'category_id': category_id,
                'category_name': category['name'],
                'color': category['color'],
                'weight': round(weight, 2),
                'time_weight': round(time_weight, 2),
                'hour': hour,
                'is_night': hour >= 22 or hour <= 5,
                'domain': str(domain),
                'subject': str(row.get('subject', ''))[:80],
            })
            
        except Exception as e:
            skipped += 1
            continue
        
        # 进度显示
        if len(results) % 5000 == 0:
            print(f"   处理中: {len(results)}...")
    
    if skipped > 0:
        print(f"   跳过无效记录: {skipped}")
    
    # 按时间排序
    results.sort(key=lambda x: x['timestamp'])
    
    # 保存 JSON
    print(f"\n💾 保存: {output_file} ({len(results)} 条)")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)
    
    # 统计
    print("\n📊 统计信息:")
    
    # 时间范围
    start_date = datetime.fromtimestamp(results[0]['timestamp'] / 1000)
    end_date = datetime.fromtimestamp(results[-1]['timestamp'] / 1000)
    print(f"   时间范围: {start_date.date()} 至 {end_date.date()}")
    
    # 类别分布
    cat_counts = {}
    for r in results:
        name = r['category_name']
        cat_counts[name] = cat_counts.get(name, 0) + 1
    
    print("\n   类别分布 (Top 10):")
    for name, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:10]:
        pct = count / len(results) * 100
        print(f"   {name}: {count:,} ({pct:.1f}%)")
    
    # 深夜比例
    night_count = sum(1 for r in results if r['is_night'])
    print(f"\n   深夜事件 (22:00-05:59): {night_count:,} ({night_count/len(results)*100:.1f}%)")
    
    # JS 配置
    js_config = f"""
// 数据配置 (自动生成)
const NOISE_DATA_CONFIG = {{
  totalRecords: {len(results)},
  timeRange: {{
    start: {results[0]['timestamp']},
    end: {results[-1]['timestamp']},
    startDate: "{start_date.date()}",
    endDate: "{end_date.date()}"
  }},
  categories: {json.dumps(CATEGORIES, ensure_ascii=False)},
  statistics: {{
    nightEvents: {night_count},
    nightRatio: {round(night_count/len(results), 3)},
    topCategories: {json.dumps(sorted(cat_counts.items(), key=lambda x: -x[1])[:5], ensure_ascii=False)}
  }}
}};
"""
    
    config_file = output_file.replace('.json', '_config.js')
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(js_config)
    print(f"\n💾 配置文件: {config_file}")
    
    return results


if __name__ == '__main__':
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'merged_noise_complaints.csv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'noise_data.json'
    
    process_data(input_file, output_file)
