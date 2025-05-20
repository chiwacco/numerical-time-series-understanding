import numpy as np
import json
import os

# ランダムな2点間の値を比較し、その結果（記号）と関連情報を新しい辞書として返す関数
def generate_comparison_and_create_dictionary(dataset): # 関数名を変更
    """
    データセット内の 'values' からランダムに選択された2点の値を比較し、
    その比較結果（'>', '<', '='）と元のデータセットの情報を合わせて新しい辞書を作成します。
    """
    if 'values' not in dataset or not dataset['values']:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。比較できません。")
        return {
            **dataset,
            'calculated_comparison_symbol': None,
            'comparison_start_index': None,
            'comparison_end_index': None,
            'value_at_start_index': None,
            'value_at_end_index': None,
        }

    # years は必須ではないが、元のスクリプトに合わせて処理
    years_list = dataset.get('years_column', [])
    years = np.array(years_list)
    values = np.array(dataset['values'], dtype=float)

    if len(values) < 2: # 2点を比較するには少なくとも2つの要素が必要
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' の 'values' の要素が2未満です。比較できません。")
        return {
            **dataset,
            'years_column': years_list,
            'values': values.tolist(),
            'calculated_comparison_symbol': None,
            'comparison_start_index': None,
            'comparison_end_index': None,
            'value_at_start_index': None,
            'value_at_end_index': None,
        }

    # start_index と end_index をランダムに生成
    # values の長さを基準にインデックスを決定
    start_index = np.random.randint(0, len(values) - 1)
    end_index = np.random.randint(start_index + 1, len(values))

    # 選択されたインデックスの値を取得
    value_at_start = values[start_index]
    value_at_end = values[end_index]

    # 値を比較して記号を決定
    if value_at_start > value_at_end:
        comparison_symbol = ">"
    elif value_at_start < value_at_end:
        comparison_symbol = "<"
    else:
        comparison_symbol = "="

    result_dictionary = {
        **dataset, # 元のデータセットのキーをすべて保持
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []),
        'values': values.tolist(), # float型に変換されたvaluesリスト
        'calculated_comparison_symbol': comparison_symbol,
        'comparison_start_index': int(start_index),     
        'comparison_end_index': int(end_index),        
        'value_at_start_index': float(value_at_start),  
        'value_at_end_index': float(value_at_end),     
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
                    if 'id' not in dataset: # IDがなければ行番号ベースで付与
                        dataset['id'] = f"line_{line_number}"
                    datasets.append(dataset)
                except json.JSONDecodeError:
                    print(f"警告: ファイル '{file_path}' の {line_number} 行目が有効なJSONではありません。スキップします: {line.strip()}")
    except IOError as e:
        print(f"エラー: ファイル '{file_path}' の読み込み中にエラーが発生しました: {e}")
        return []
    return datasets

if __name__ == "__main__":
    input_jsonl_file = "test.jsonl" 

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)

    if not datasets_from_file:
        print("処理するデータセットがありませんでした。")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件のデータセットを読み込みました。\n")

        processed_results = []
        for i, dataset_doc in enumerate(datasets_from_file):
            print(f"--- データセット {i+1} (ID: {dataset_doc.get('id', 'N/A')}) の処理 ---")
            dictionary_with_comparison = generate_comparison_and_create_dictionary(dataset_doc)
            processed_results.append(dictionary_with_comparison)

            print("値の比較結果が追加された辞書:")
            print(json.dumps(dictionary_with_comparison, indent=4, ensure_ascii=False))
            if dictionary_with_comparison.get('calculated_comparison_symbol') is not None:
                start_idx_val = dictionary_with_comparison['value_at_start_index']
                end_idx_val = dictionary_with_comparison['value_at_end_index']
                symbol = dictionary_with_comparison['calculated_comparison_symbol']
                print(f"値 {start_idx_val} (idx: {dictionary_with_comparison['comparison_start_index']}) と "
                      f"値 {end_idx_val} (idx: {dictionary_with_comparison['comparison_end_index']}) の比較結果: {symbol}")
            elif 'values' in dataset_doc and not dataset_doc['values']:
                 print("比較は実行されませんでした (valuesが空でした)。")
            elif 'values' not in dataset_doc or len(dataset_doc.get('values',[])) < 2 :
                 print("比較は実行されませんでした (valuesキーがないか、要素数が2未満でした)。")
            print("-" * 20)
            print("\n")

        output_jsonl_file = "comparison_output.jsonl"
        try:
            with open(output_jsonl_file, 'w', encoding='utf-8') as outfile:
                for result_item in processed_results:
                    outfile.write(json.dumps(result_item, ensure_ascii=False) + '\n')
            print(f"処理結果 (値の比較結果を含む) を '{output_jsonl_file}' に書き出しました。") 
        except IOError as e:
            print(f"エラー: 結果のファイル '{output_jsonl_file}'への書き出し中にエラーが発生しました: {e}")
