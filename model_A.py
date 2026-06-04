# -*- coding: utf-8 -*-
"""
方案A：数值特征单模态分类模型
基于XGBoost实现啤酒风格分类
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import xgboost as xgb
import joblib

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

# ==================== 数据预处理 ====================
def preprocess_data(df):
    """数据预处理 - 修复类型错误"""
    # 核心数值特征
    numeric_features = ['abv', 'ibu']
    # 核心分类特征
    categorical_features = ['srmId', 'glasswareId', 'availableId']
    
    # 将字符串类型的数值列转换为float（处理可能的字符串格式）
    for col in numeric_features:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 数值列：中位数填充空值
    df[numeric_features] = df[numeric_features].fillna(df[numeric_features].median())
    
    # 分类列：先转字符串填充缺失值，再用LabelEncoder转为整数（XGBoost需要数值类型）
    cat_encoders = {}
    for col in categorical_features:
        df[col] = df[col].astype(str).fillna("-1")
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        cat_encoders[col] = le
    
    # 标签编码
    label_encoder = LabelEncoder()
    df['styleId'] = label_encoder.fit_transform(df['styleId'].astype(str))
    
    # 特征合并（排除styleId）
    X = df[numeric_features + categorical_features]
    y = df['styleId']
    
    # 标准化数值特征
    scaler = StandardScaler()
    X[numeric_features] = scaler.fit_transform(X[numeric_features])
    
    return X, y, label_encoder, scaler

# ==================== 模型训练 ====================
def train_model(X_train, y_train):
    """训练XGBoost模型"""
    params = {
        'objective': 'multi:softmax',
        'num_class': len(np.unique(y_train)),
        'eval_metric': 'mlogloss',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42
    }
    
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    return model

# ==================== 模型评估 ====================
def evaluate_model(model, X_test, y_test, label_encoder):
    """评估模型性能"""
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"准确率: {accuracy:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")
    print(f"Weighted-F1: {weighted_f1:.4f}")
    
    # 输出混淆矩阵（前10个类别）
    cm = confusion_matrix(y_test, y_pred)
    print("\n混淆矩阵（部分）:")
    print(cm[:10, :10])
    
    return {
        'accuracy': accuracy,
        'macro_f1': macro_f1,
        'weighted_f1': weighted_f1,
        'confusion_matrix': cm
    }

# ==================== 主函数 ====================
def main():
    # 配置
    json_dir = 'data/beer-dataset-master/beer-database'
    model_save_path = 'models/model_a_xgboost.pkl'
    encoder_save_path = 'models/label_encoder_a.pkl'
    scaler_save_path = 'models/scaler_a.pkl'
    
    # 创建保存目录
    os.makedirs('models', exist_ok=True)
    
    # 加载数据
    print("加载数据...")
    df = load_data(json_dir)
    print(f"加载完成，共 {len(df)} 条记录")
    
    # 数据预处理
    print("数据预处理...")
    X, y, label_encoder, scaler = preprocess_data(df)
    
    # 处理类别不平衡问题：过滤样本数少于2的类别
    print("检查类别分布...")
    unique, counts = np.unique(y, return_counts=True)
    class_counts = dict(zip(unique, counts))
    print(f"总类别数: {len(class_counts)}")
    
    # 找出样本数 >= 2 的类别
    valid_classes = [cls for cls, cnt in class_counts.items() if cnt >= 2]
    print(f"有效类别数（样本数>=2）: {len(valid_classes)}")
    
    # 过滤数据
    mask = np.isin(y, valid_classes)
    X = X[mask]
    y = y[mask]
    print(f"过滤后样本数: {len(y)}")
    
    # 重新编码标签，使其连续（XGBoost要求类别从0开始连续）
    print("重新编码标签...")
    label_encoder_final = LabelEncoder()
    y = label_encoder_final.fit_transform(y)
    print(f"重新编码后类别数: {len(np.unique(y))}")
    
    # 数据集划分（分层抽样）
    print("划分数据集...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # 训练模型
    print("训练模型...")
    model = train_model(X_train, y_train)
    
    # 评估模型
    print("\n模型评估:")
    results = evaluate_model(model, X_test, y_test, label_encoder_final)
    
    # 保存模型
    print("\n保存模型...")
    joblib.dump(model, model_save_path)
    joblib.dump(label_encoder_final, encoder_save_path)
    joblib.dump(scaler, scaler_save_path)
    print(f"模型已保存到 {model_save_path}")
    
    # 特征重要性
    print("\n特征重要性:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance)

if __name__ == '__main__':
    main()
