import numpy as np
import json
import os

# ランダムな2点間の差分を計算し、関連情報と共に新しい辞書として返す関数
def generate_difference_and_create_dictionary(dataset):
    """
    データセット内の 'values' からランダムに選択された2点間の値の差（絶対値）を計算し、
    元のデータセットの情報と合わせて新しい辞書を作成します。
    """
    if 'values' not in dataset or not dataset['values']:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。差分を計算できません。")
        return {
            **dataset,
            'calculated_difference': None,
            'difference_start_index': None,
            'difference_end_index': None,
        }

    years_list = dataset.get('years_column', []) # yearsは差分計算に直接使わないが保持
    years = np.array(years_list)
    values = np.array(dataset['values'], dtype=float)

    if len(values) < 2: # 2点間の差分を取るには少なくとも2つの要素が必要
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' の 'values' の要素が2未満です。差分を計算できません。")
        return {
            **dataset,
            'years_column': years_list,
            'values': values.tolist(),
            'calculated_difference': None,
            'difference_start_index': None,
            'difference_end_index': None,
        }

    # start_index と end_index をランダムに生成
    # values の長さを基準にインデックスを決定
    start_index = np.random.randint(0, len(values) - 1)
    end_index = np.random.randint(start_index + 1, len(values))

    # 差分を計算
    difference = abs(values[end_index] - values[start_index])

    result_dictionary = {
        **dataset,
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []),
        'values': values.tolist(),
        'calculated_difference': difference,
        'difference_start_index': int(start_index),
        'difference_end_index': int(end_index),
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
    input_jsonl_file = "test_for_difference.jsonl"

    if not os.path.exists(input_jsonl_file):
        sample_data = [{"id": "diff_sample_1", "values": [10, 20, 15, 30, 25, 40, 35]}]
        try:
            with open(input_jsonl_file, 'w', encoding='utf-8') as f:
                for item in sample_data: f.write(json.dumps(item) + '\n')
            print(f"サンプル入力ファイル '{input_jsonl_file}' を作成しました。\n")
        except IOError: print(f"サンプルファイル '{input_jsonl_file}' 作成失敗.\n")

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)
    if not datasets_from_file: print("処理データなし.")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件読込.\n")
        results = [generate_difference_and_create_dictionary(ds) for ds in datasets_from_file]
        for i, res_dict in enumerate(results):
            print(f"--- データセット {i+1} (ID: {res_dict.get('id', 'N/A')}) ---")
            print(json.dumps(res_dict, indent=4, ensure_ascii=False))
            if res_dict.get('calculated_difference') is not None:
                s_idx, e_idx = res_dict['difference_start_index'], res_dict['difference_end_index']
                print(f"範囲 [{s_idx}:{e_idx}] の差分: {res_dict['calculated_difference']}")
            print("-" * 20 + "\n")

        output_file = "dif_output.jsonl"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in results: f.write(json.dumps(item) + '\n')
            print(f"処理結果を '{output_file}' に書き出し.")
        except IOError as e: print(f"'{output_file}' 書出エラー: {e}")