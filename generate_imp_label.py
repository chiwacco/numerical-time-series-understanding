import numpy as np
import json
import os
import random 
import pandas as pd 

def generate_interpolation_and_create_dictionary(dataset):
    """
    データセット内の 'values' のランダムな位置（最初と最後を除く）にNaNを1つ挿入し、
    線形補完を行って補間値を計算し、新しい辞書を作成します。
    """
    original_values_list = dataset.get('values', [])
    if not original_values_list: # valuesがないか空の場合
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。補間処理できません。")
        return {
            **dataset,
            'original_values': [],
            'values_with_nan_display': [],
            'nan_index': -1,
            'gold_interpolated_value': None,
        }

    original_values = np.array(original_values_list, dtype=float)
    years_list = dataset.get('years_column', [])
    years = np.array(years_list)

    if len(original_values) < 3:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' の 'values' の要素が3未満です。内部にNaNを挿入して補間できません。")
        return {
            **dataset,
            'original_values': original_values.tolist(),
            'values_with_nan_display': [str(v) for v in original_values.tolist()], # 表示用に文字列化
            'nan_index': -1, # NaNを挿入できなかったことを示す
            'gold_interpolated_value': None,
            'years_column': years_list,
        }

    values_with_nan_array = original_values.copy()
    
    nan_index = random.randint(1, len(values_with_nan_array) - 2)
    values_with_nan_array[nan_index] = np.nan

    # pandas Seriesを使って線形補完
    series_with_nan = pd.Series(values_with_nan_array)
    interpolated_series = series_with_nan.interpolate(method='linear')
    gold_interpolated_value = interpolated_series[nan_index]

    if pd.isna(gold_interpolated_value): # 通常は起こりにくいが念のため
        gold_interpolated_value = None
        print(f"補間失敗: データセットID '{dataset.get('id', 'N/A')}' nan_index: {nan_index}")

    values_for_llm_display = [str(x) if not pd.isna(x) else "NaN" for x in values_with_nan_array.tolist()]

    result_dictionary = {
        **dataset,
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []),
        'original_values': original_values.tolist(), # 元のvalues (floatのリスト)
        'values_with_nan_display': values_for_llm_display, # NaN挿入後の表示用リスト
        'nan_index': nan_index, # NaNを挿入したインデックス
        'gold_interpolated_value': float(gold_interpolated_value) if gold_interpolated_value is not None else None, # 補間された値
    }
    return result_dictionary

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
    input_jsonl_file = "test_for_interpolation.jsonl"

    if not os.path.exists(input_jsonl_file):
        sample_data = [
            {"id": "interp_sample_1", "values": [10.0, 20.0, 0 , 40.0, 50.0]}, # 0をNaNに置き換えて補間する例 (index 2)
            {"id": "interp_sample_2", "values": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]}
        ]
        try:
            with open(input_jsonl_file, 'w', encoding='utf-8') as f:
                for item in sample_data: f.write(json.dumps(item) + '\n')
            print(f"サンプル入力ファイル '{input_jsonl_file}' を作成しました。\n")
        except IOError: print(f"サンプルファイル '{input_jsonl_file}' 作成失敗.\n")

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)
    if not datasets_from_file: print("処理データなし.")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件読込.\n")
        results = [generate_interpolation_and_create_dictionary(ds) for ds in datasets_from_file]
        for i, res_dict in enumerate(results):
            print(f"--- データセット {i+1} (ID: {res_dict.get('id', 'N/A')}) ---")
            print(json.dumps(res_dict, indent=4, ensure_ascii=False))
            if res_dict.get('gold_interpolated_value') is not None:
                print(f"NaN挿入位置: {res_dict['nan_index']}")
                print(f"補間された値: {res_dict['gold_interpolated_value']}")
            print("-" * 20 + "\n")

        output_file = "interpolation_output.jsonl"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in results: f.write(json.dumps(item) + '\n')
            print(f"処理結果を '{output_file}' に書き出し.")
        except IOError as e: print(f"'{output_file}' 書出エラー: {e}")