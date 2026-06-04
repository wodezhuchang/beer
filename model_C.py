# -*- coding: utf-8 -*-
"""
方案C：多模态融合分类模型
融合数值特征和文本特征实现啤酒风格分类
"""

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
from torch.optim import AdamW
from tqdm import tqdm

# ==================== 数据加载 ====================
def load_data(json_dir):
    """加载所有JSON文件并合并"""
    data = []
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(json_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if 'data' in content:
                        data.extend(content['data'])
            except Exception as e:
                print(f"加载文件失败 {filename}: {e}")
    return pd.DataFrame(data)

# ==================== 数据集类 ====================
class BeerMultimodalDataset(Dataset):
    def __init__(self, texts, numeric_features, labels, tokenizer, max_len=128):
        self.texts = texts
        self.numeric_features = numeric_features
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        numeric = self.numeric_features[idx]
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'numeric_features': torch.tensor(numeric, dtype=torch.float),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# ==================== 多模态融合模型 ====================
class MultimodalModel(nn.Module):
    def __init__(self, num_classes, bert_model_name='bert-base-uncased', numeric_dim=5):
        super(MultimodalModel, self).__init__()
        
        # BERT文本分支
        self.bert = BertModel.from_pretrained(bert_model_name)
        self.bert_hidden_size = self.bert.config.hidden_size
        
        # 数值特征分支
        self.numeric_fc = nn.Sequential(
            nn.Linear(numeric_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        
        # 融合层
        self.fusion_size = self.bert_hidden_size + 32
        self.fusion_fc = nn.Sequential(
            nn.Linear(self.fusion_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        # 分类头
        self.classifier = nn.Linear(128, num_classes)
    
    def forward(self, input_ids, attention_mask, numeric_features):
        # BERT编码
        bert_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        cls_token = bert_output.last_hidden_state[:, 0, :]  # [CLS] token
        
        # 数值特征处理
        numeric_output = self.numeric_fc(numeric_features)
        
        # 特征融合
        fused = torch.cat([cls_token, numeric_output], dim=1)
        fused = self.fusion_fc(fused)
        
        # 分类
        logits = self.classifier(fused)
        
        return logits

# ==================== 训练函数 ====================
def train_epoch(model, data_loader, optimizer, device, scheduler, criterion):
    model.train()
    total_loss = 0
    predictions = []
    true_labels = []
    
    for batch in tqdm(data_loader, desc="训练中"):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        numeric_features = batch['numeric_features'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        logits = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            numeric_features=numeric_features
        )
        
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        
        total_loss += loss.item()
        
        preds = torch.argmax(logits, dim=1).cpu().numpy()
        predictions.extend(preds)
        true_labels.extend(labels.cpu().numpy())
    
    avg_loss = total_loss / len(data_loader)
    accuracy = accuracy_score(true_labels, predictions)
    
    return avg_loss, accuracy

# ==================== 评估函数 ====================
def eval_epoch(model, data_loader, device, criterion):
    model.eval()
    total_loss = 0
    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for batch in tqdm(data_loader, desc="评估中"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            numeric_features = batch['numeric_features'].to(device)
            labels = batch['labels'].to(device)
            
            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                numeric_features=numeric_features
            )
            
            loss = criterion(logits, labels)
            total_loss += loss.item()
            
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            predictions.extend(preds)
            true_labels.extend(labels.cpu().numpy())
    
    avg_loss = total_loss / len(data_loader)
    accuracy = accuracy_score(true_labels, predictions)
    macro_f1 = f1_score(true_labels, predictions, average='macro')
    weighted_f1 = f1_score(true_labels, predictions, average='weighted')
    
    return avg_loss, accuracy, macro_f1, weighted_f1

# ==================== 主函数 ====================
def main():
    # 配置
    json_dir = 'data/beer-dataset-master/beer-database'
    bert_model_name = 'bert-base-uncased'
    max_len = 128
    batch_size = 16
    epochs = 5
    learning_rate = 1e-4
    
    # 数值特征列表
    numeric_cols = ['abv', 'ibu', 'srmId', 'glasswareId', 'availableId']
    
    # 设备配置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建保存目录
    os.makedirs('models', exist_ok=True)
    
    # 加载数据
    print("加载数据...")
    df = load_data(json_dir)
    print(f"加载完成，共 {len(df)} 条记录")
    
    # 过滤缺失关键数据
    initial_len = len(df)
    df = df[df['description'].notna() & (df['description'] != '')]
    print(f"过滤空描述后，共 {len(df)} 条记录（移除 {initial_len - len(df)} 条）")
    
    # 过滤缺失标签的数据
    initial_len = len(df)
    df = df[df['styleId'].notna()]
    print(f"过滤空标签后，共 {len(df)} 条记录（移除 {initial_len - len(df)} 条）")
    
    # 处理数值特征：转换为数值类型
    print("处理数值特征...")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 填充缺失值
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    print("数值特征缺失值已填充")
    
    # 标签编码
    label_encoder = LabelEncoder()
    df['styleId'] = label_encoder.fit_transform(df['styleId'].astype(str))
    num_classes = len(label_encoder.classes_)
    print(f"类别数量: {num_classes}")
    
    # 处理类别不平衡问题：过滤样本数少于2的类别
    print("检查类别分布...")
    unique, counts = np.unique(df['styleId'], return_counts=True)
    class_counts = dict(zip(unique, counts))
    valid_classes = [cls for cls, cnt in class_counts.items() if cnt >= 2]
    print(f"有效类别数（样本数>=2）: {len(valid_classes)}")
    
    # 过滤数据
    initial_len = len(df)
    df = df[np.isin(df['styleId'], valid_classes)]
    print(f"过滤稀有类别后，共 {len(df)} 条记录（移除 {initial_len - len(df)} 条）")
    
    # 重新编码标签，使其连续（适配PyTorch分类头）
    print("重新编码标签...")
    label_encoder = LabelEncoder()
    df['styleId'] = label_encoder.fit_transform(df['styleId'])
    num_classes = len(label_encoder.classes_)
    print(f"重新编码后类别数: {num_classes}")
    
    # 标准化数值特征
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    print("数值特征已标准化")
    
    # 数据集划分
    print("划分数据集...")
    X_text_train, X_text_test, X_numeric_train, X_numeric_test, y_train, y_test = train_test_split(
        df['description'].values,
        df[numeric_cols].values,
        df['styleId'].values,
        test_size=0.3,
        random_state=42,
        stratify=df['styleId'].values
    )
    
    print(f"训练集: {len(X_text_train)} 条, 测试集: {len(X_text_test)} 条")
    
    # 加载tokenizer
    print("加载BERT Tokenizer...")
    tokenizer = BertTokenizer.from_pretrained(bert_model_name)
    
    # 创建数据加载器
    train_dataset = BeerMultimodalDataset(
        X_text_train, X_numeric_train, y_train, tokenizer, max_len
    )
    test_dataset = BeerMultimodalDataset(
        X_text_test, X_numeric_test, y_test, tokenizer, max_len
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # 初始化模型
    print("初始化多模态模型...")
    model = MultimodalModel(
        num_classes=num_classes,
        bert_model_name=bert_model_name,
        numeric_dim=len(numeric_cols)
    ).to(device)
    
    # 优化器和调度器
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    total_steps = len(train_loader) * epochs
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, total_steps)
    criterion = nn.CrossEntropyLoss()
    
    # 训练循环
    print("开始训练...")
    for epoch in range(epochs):
        print(f"\n===== 第 {epoch+1}/{epochs} 轮 =====")
        
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, device, scheduler, criterion)
        print(f"训练损失: {train_loss:.4f}, 训练准确率: {train_acc:.4f}")
        
        val_loss, val_acc, val_macro_f1, val_weighted_f1 = eval_epoch(model, test_loader, device, criterion)
        print(f"验证损失: {val_loss:.4f}, 验证准确率: {val_acc:.4f}")
        print(f"验证Macro-F1: {val_macro_f1:.4f}, 验证Weighted-F1: {val_weighted_f1:.4f}")
    
    # 最终评估
    print("\n===== 最终评估 =====")
    test_loss, test_acc, test_macro_f1, test_weighted_f1 = eval_epoch(model, test_loader, device, criterion)
    print(f"测试损失: {test_loss:.4f}")
    print(f"测试准确率: {test_acc:.4f}")
    print(f"测试Macro-F1: {test_macro_f1:.4f}")
    print(f"测试Weighted-F1: {test_weighted_f1:.4f}")
    
    # 保存模型
    print("\n保存模型...")
    torch.save(model.state_dict(), 'models/model_c_multimodal.pth')
    tokenizer.save_pretrained('models/model_c_tokenizer')
    torch.save(label_encoder, 'models/label_encoder_c.pth')
    torch.save(scaler, 'models/scaler_c.pth')
    print("模型已保存到 models/")

if __name__ == '__main__':
    main()
