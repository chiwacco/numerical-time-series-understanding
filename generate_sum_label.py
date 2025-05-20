import numpy as np
import json
import os 

# gold（最大値）を生成し、関連情報と共に新しい辞書として返す関数
def generate_gold_and_create_dictionary(dataset):
    """
    データセット内の 'values' から最大値（gold）を計算し、
    元のデータセットの情報と合わせて新しい辞書を作成します。
    """
    if 'values' not in dataset or not dataset['values']:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。goldを生成できません。")
        return {
            **dataset,
            'calculated_gold_value': None,
        }

    years = np.array(dataset.get('years_column', []))
    values = np.array(dataset['values'], dtype=float)

    calculated_gold = np.sum(values)

    result_dictionary = {
        **dataset,
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []),
        'values': values.tolist(),
        'calculated_gold_value': calculated_gold,
    }
    return result_dictionary

# JSONLファイルからデータセットを読み込む関数
def load_datasets_from_jsonl(file_path):
    """
    JSONLファイルからデータセットのリストを読み込みます。
    1行に1つのJSONオブジェクトが含まれている形式を想定しています。
    """
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
    # ★★★ 入力するJSONLファイル名を指定してください ★★★
    input_jsonl_file = "test.jsonl" 

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)

    if not datasets_from_file:
        print("処理するデータセットがありませんでした。")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件のデータセットを読み込みました。\n")

        processed_results = []
        for i, dataset_doc in enumerate(datasets_from_file):
            print(f"--- データセット {i+1} (ID: {dataset_doc.get('id', 'N/A')}) の処理 ---")
            dictionary_with_gold = generate_gold_and_create_dictionary(dataset_doc)
            processed_results.append(dictionary_with_gold)

            print("生成されたgoldが追加された辞書:")
            print(json.dumps(dictionary_with_gold, indent=4, ensure_ascii=False))
            if dictionary_with_gold.get('calculated_gold_value') is not None:
                print(f"抽出されたgoldの値: {dictionary_with_gold['calculated_gold_value']}")
            elif 'values' in dataset_doc and not dataset_doc['values']:
                 print("goldの値は計算されませんでした (valuesが空でした)。")
            elif 'values' not in dataset_doc:
                 print("goldの値は計算されませんでした (valuesキーがありませんでした)。")
            print("-" * 20)
            print("\n")

        output_jsonl_file = "sum_with_gold.jsonl"
        try:
            with open(output_jsonl_file, 'w', encoding='utf-8') as outfile:
                for result_item in processed_results:
                    # 各処理結果の辞書をJSON文字列に変換してファイルに書き込む
                    outfile.write(json.dumps(result_item, ensure_ascii=False) + '\n')
            print(f"処理結果を '{output_jsonl_file}' に書き出しました。")
        except IOError as e:
            print(f"エラー: 結果のファイル '{output_jsonl_file}'への書き出し中にエラーが発生しました: {e}")
