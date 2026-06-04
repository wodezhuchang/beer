# -*- coding: utf-8 -*-
"""
方案B：文本特征单模态分类模型
基于BERT实现啤酒风格分类
"""

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
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
class BeerDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        # 修复这里
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
            'labels': torch.tensor(label, dtype=torch.long)
        }
# ==================== 训练函数 ====================
def train_epoch(model, data_loader, optimizer, device, scheduler, criterion):
    model.train()
    total_loss = 0
    predictions = []
    true_labels = []
    
    for batch in tqdm(data_loader, desc="训练中"):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        logits = outputs.logits
        
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
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            logits = outputs.logits
            
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
    model_name = 'bert-base-uncased'
    max_len = 128
    batch_size = 16
    epochs = 3
    learning_rate = 2e-5
    
    # 设备配置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建保存目录
    os.makedirs('models', exist_ok=True)
    
    # 加载数据
    print("加载数据...")
    df = load_data(json_dir)
    print(f"加载完成，共 {len(df)} 条记录")
    
    # 过滤缺失描述的数据
    initial_len = len(df)
    df = df[df['description'].notna() & (df['description'] != '')]
    print(f"过滤空描述后，共 {len(df)} 条记录（移除 {initial_len - len(df)} 条）")
    
    # 过滤缺失标签的数据
    initial_len = len(df)
    df = df[df['styleId'].notna()]
    print(f"过滤空标签后，共 {len(df)} 条记录（移除 {initial_len - len(df)} 条）")
    
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
    
    # 数据集划分
    print("划分数据集...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['description'].values, 
        df['styleId'].values, 
        test_size=0.3, 
        random_state=42,
        stratify=df['styleId'].values
    )
    
    print(f"训练集: {len(X_train)} 条, 测试集: {len(X_test)} 条")
    
    # 加载tokenizer
    print("加载BERT Tokenizer...")
    tokenizer = BertTokenizer.from_pretrained(model_name)
    
    # 创建数据加载器
    train_dataset = BeerDataset(X_train, y_train, tokenizer, max_len)
    test_dataset = BeerDataset(X_test, y_test, tokenizer, max_len)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # 加载预训练模型
    print("加载BERT模型...")
    model = BertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_classes
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
    model.save_pretrained('models/model_b_bert')
    tokenizer.save_pretrained('models/model_b_bert')
    torch.save(label_encoder, 'models/label_encoder_b.pth')
    print("模型已保存到 models/model_b_bert")

if __name__ == '__main__':
    main()
