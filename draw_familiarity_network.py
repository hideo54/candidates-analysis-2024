#%%
import collections

import japanize_matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

questionnaire_df = pd.read_csv('questionnaire_2024.csv').set_index('整理番号')

party_code_to_name = questionnaire_df[['集計党派CD', '集計党派']].drop_duplicates().set_index('集計党派CD').sort_index().to_dict()['集計党派']

def get_edges(row):
    self_party_code = int(row['集計党派CD'])
    if self_party_code == 10 or self_party_code == 11: # 諸派・無所属の回答は含めない
        return []
    q27_answers = [row[f'Q27\n-{i:02}'] for i in range(1, 11)]
    edges = [(self_party_code, int(a)) for a in q27_answers if not pd.isna(a)]
    return edges

all_edges = [edge for _, row in questionnaire_df.iterrows() for edge in get_edges(row)]
edge_counts = collections.Counter(all_edges)

party_candidates_count = questionnaire_df['集計党派CD'].value_counts().sort_index()
party_incumbents_count = questionnaire_df[questionnaire_df['新旧'] == 1]['集計党派CD'].value_counts().sort_index()

party_name_to_color = {
    '自民党': '#d7033a',
    '公明党': '#f55881',
    '立憲民主党': '#004098',
    '日本維新の会': '#36c200',
    '共産党': '#7957da',
    '国民民主党': '#f8bc00',
    'れいわ新選組': '#e5007f',
    '社民党': '#01a8ec',
    '参政党': '#ed6c00',
    '諸派': '#777777',
    '無所属': '#777777',
}

party_code_to_color = {
    code: party_name_to_color[name]
    for code, name in party_code_to_name.items()
}

G = nx.DiGraph()

for edge, count in edge_counts.items():
    G.add_edge(*edge, weight=count)

node_colors = [party_code_to_color[node] for node in G.nodes()]
node_sizes = [
    20 * (party_incumbents_count[node] if node in party_incumbents_count else 0)
    for node in G.nodes()
]

# edge_widths = [0.05 * G[u][v]['weight'] for u, v in G.edges()] # 矢印の太さを総数にする場合
edge_widths = [10 * G[u][v]['weight'] / party_candidates_count[u] for u, v in G.edges()] # 矢印の太さを割合にする場合

spring_layout_seed = 16 # これはかなりシードゲー。矢印が重ならない・近い政党が近く配置される、を条件に 0-20 を見て決めた
pos = nx.spring_layout(G, k=10, seed=spring_layout_seed)

plt.figure(figsize=(8, 6))

nx.draw(
    G,
    pos,
    connectionstyle='arc3,rad=0.3',
    arrowsize=30,
    node_color=node_colors,
    node_size=node_sizes,
    width=edge_widths,
    edge_color='#cccccc',
)

labels = {code: party_code_to_name[code] for code in G.nodes()}
nx.draw_networkx_labels(
    G,
    pos,
    labels=labels,
    font_size=10,
    font_family='Noto Sans CJK JP',
)

plt.title('各政党の候補者はどの政党と連携したいか?', fontsize=20)
plt.figtext(
    0.5,
    -0.1,
    'データ: 読売新聞 衆院選2024 候補者アンケート (23日15時30分時点)\n'
    + '点の大きさは前職議員の数、矢印の太さは各党候補者の回答割合に対応',
    horizontalalignment='center',
    fontsize=10,
)
plt.savefig('familiarity-network.png', bbox_inches='tight')

# %%
