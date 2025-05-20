import numpy as np
import json
import os

# 閾値を超える値を検出し、関連情報と共に新しい辞書として返す関数
def generate_threshold_values_and_create_dictionary(dataset):
    """
    データセット内の 'values' からランダムな閾値を設定し、
    その閾値を超える値のリストを計算し、新しい辞書を作成します。
    """
    if 'values' not in dataset or not dataset['values']:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。処理できません。")
        return {
            **dataset,
            'threshold_value': None,
            'values_above_threshold': [],
        }

    years_list = dataset.get('years_column', [])
    years = np.array(years_list)
    values = np.array(dataset['values'], dtype=float)

    if len(values) == 0: # valuesが空の配列の場合
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' の 'values' が空です。処理できません。")
        return {
            **dataset,
            'years_column': years_list,
            'values': [],
            'threshold_value': None,
            'values_above_threshold': [],
        }

    
    min_val, max_val = values.min(), values.max()
    if min_val == max_val:
       
        threshold_val = round(min_val, 1)
    else:
        threshold_val = round(np.random.uniform(min_val, max_val), 1)

    # 閾値を超える値を取得
    values_above = values[values > threshold_val].tolist()

    result_dictionary = {
        **dataset,
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []),
        'values': values.tolist(),
        'threshold_value': threshold_val,
        'values_above_threshold': values_above,
    }
    return result_dictionary

# JSONLファイルからデータセットを読み込む関数 (変更なし、上記からコピー)
def load_datasets_from_jsonl(file_path):
    datasets = []
    if not os.path.exists(file_path):
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
        return datasets
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                try:
                    dataset = json.loads(line)
                    if 'id' not in dataset:
                        dataset['id'] = f"line_{line_number}"
                    datasets.append(dataset)
                except json.JSONDecodeError:
                    print(f"警告: ファイル '{file_path}' の {line_number} 行目が有効なJSONではありません。スキップします: {line.strip()}")
    except IOError as e:
        print(f"エラー: ファイル '{file_path}' の読み込み中にエラーが発生しました: {e}")
        return []
    return datasets

if __name__ == "__main__":
    input_jsonl_file = "test_for_threshold.jsonl"

    if not os.path.exists(input_jsonl_file):
        sample_data = [{"id": "thresh_sample_1", "values": [10, 20, 15, 30, 25, 40, 35]}]
        try:
            with open(input_jsonl_file, 'w', encoding='utf-8') as f:
                for item in sample_data: f.write(json.dumps(item) + '\n')
            print(f"サンプル入力ファイル '{input_jsonl_file}' を作成しました。\n")
        except IOError: print(f"サンプルファイル '{input_jsonl_file}' 作成失敗.\n")

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)
    if not datasets_from_file: print("処理データなし.")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件読込.\n")
        results = [generate_threshold_values_and_create_dictionary(ds) for ds in datasets_from_file]
        for i, res_dict in enumerate(results):
            print(f"--- データセット {i+1} (ID: {res_dict.get('id', 'N/A')}) ---")
            print(json.dumps(res_dict, indent=4, ensure_ascii=False))
            if res_dict.get('threshold_value') is not None:
                print(f"閾値: {res_dict['threshold_value']}")
                print(f"閾値を超える値: {res_dict['values_above_threshold']}")
            print("-" * 20 + "\n")

        output_file = "threshold_output.jsonl"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in results: f.write(json.dumps(item) + '\n')
            print(f"処理結果を '{output_file}' に書き出し.")
        except IOError as e: print(f"'{output_file}' 書出エラー: {e}")