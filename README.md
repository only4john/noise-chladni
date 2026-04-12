# 城市共振：时空噪声色谱

> Urban Resonance: Spatiotemporal Noise Chromatography

利用三年的城市噪声投诉数据，结合克拉尼图形 (Chladni Figures) 的物理原理，在真实的城市底图上实现动态、艺术化的噪声可视化系统。

![Demo Preview](preview.png)

## 🌟 项目特色

### 视觉美学 - "重墨" 质感
- 矿物色谱：18 类噪声对应 18 种传统矿物色彩
- 宣纸洇墨：线条边缘带有自然的扩散效果
- 克拉尼波纹：投诉点产生类似金属粉末在振动板上的图案

### 物理仿真
- **指数衰减**：噪声随距离扩散而减弱
- **频率响应**：低频（施工）穿透力强，高频（生活）局促
- **深夜加成**：22:00-05:00 噪声穿透力 ×3
- **余震效果**：克拉尼波纹 3-5 次颤动回弹

## 🛠 技术栈

| 层级 | 技术 | 作用 |
|------|------|------|
| 底图 | Mapbox GL JS | 城市底图 + 坐标转换 |
| 渲染层 | p5.js (Canvas) | 艺术化噪声可视化 |
| 数据 | JSON | 预处理后的噪声事件 |

## 📁 文件结构

```
urban-resonance/
├── index.html          # 主程序 (三步合一)
├── preprocess.py       # 数据预处理脚本
├── README.md           # 本文档
└── noise_data.json     # 预处理后的数据 (需生成)
```

## 🚀 快速开始

### 1. 启动本地服务器

```bash
cd urban-resonance
python -m http.server 8080
```

然后访问: http://localhost:8080

### 2. 数据预处理

如果你有原始噪声投诉数据 (CSV 格式，需包含 `lon`, `lat`, `Event_time` 字段):

```bash
python preprocess.py your_data.csv -o noise_data.json
```

或生成演示数据:

```bash
python preprocess.py
```

### 3. 替换 Mapbox Token

在 `index.html` 中替换 `CONFIG.mapboxToken` 为你的 Mapbox token:

```javascript
mapboxToken: 'pk.your_token_here'
```

## 🎨 18 类矿物色谱

| ID | 类别 | 颜色 | 穿透力 |
|----|------|------|--------|
| 0-2 | 施工类 | 石青、石绿、石蓝 | ★★★★★ |
| 3-5 | 工业类 | 焦墨、煤黑、玄青 | ★★★★★ |
| 6-8 | 交通类 | 铅灰、铁灰、银灰 | ★★★★ |
| 9-11 | 社会类 | 曙红、朱砂、胭脂 | ★★★ |
| 12-14 | 生活类 | 赭石、茶色、檀棕 | ★★ |
| 15-17 | 公共类 | 紫檀、青紫、藕荷 | ★★★-★★★★ |

## 🔬 物理参数

### 时间权重 (深夜加成)

```
22:00 - 05:59  ████████████████  3.0x (深夜)
18:00 - 21:59  ████████░░░░░░░░  1.5x - 3.0x (黄昏渐变)
其他时间        ████░░░░░░░░░░░  1.0x (标准)
```

### 穿透半径

| 类别 | 基础半径 | 说明 |
|------|----------|------|
| 施工/工业 | 2000-2500m | 低频，穿透力强 |
| 交通/公共 | 1000-1800m | 中频 |
| 社会/生活 | 300-800m | 高频，局促 |

## 📐 实现步骤

### Step 1: 地图 + 坐标转换
- Mapbox 暗色底图
- `map.project([lon, lat])` 经纬度 → 像素

### Step 2: 脉冲物理模型
- `Pulse` 类：单次激发 + 指数衰减 + 余震
- 克拉尼波纹生成

### Step 3: 完整系统
- 18 类矿物色
- 深夜加成逻辑
- 克拉尼粒子系统

## 🎮 操作说明

1. **播放/暂停**：点击「播放」按钮启动时间轴
2. **时间轴**：观察 2022-2024 三年噪声事件
3. **克拉尼图案**：脉冲产生的同心波纹

## 🔧 自定义

### 修改中心位置

```javascript
CONFIG.center = [your_lon, your_lat]; // 默认: 武汉 [114.3055, 30.5928]
```

### 调整播放速度

```javascript
CONFIG.playSpeed = 100; // 默认: 100天/秒
```

### 修改颜色方案

编辑 `MINERAL_COLORS` 数组，替换 RGB 值。

## 📝 数据格式

预处理后的 JSON 格式:

```json
{
  "lon": 114.3055,
  "lat": 30.5928,
  "timestamp": 1704067200000,
  "category_id": 0,
  "category_name": "基础施工",
  "weight": 15.0,
  "is_night": false
}
```

## 📚 相关资源

- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [p5.js](https://p5js.org/reference/)
- [克拉尼图形原理](https://en.wikipedia.org/wiki/Chladni_figure)

## 📄 License

MIT License - 费腾 & Mia
