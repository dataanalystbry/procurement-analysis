import os
import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

N_PO = 5000
os.makedirs('data/raw', exist_ok=True)

names = [
    'Apex Components', 'Boreal Metals', 'Caribe Electronics', 'Delta Fasteners',
    'Echo Cable Co', 'Frontier Plastics', 'Gulf Precision', 'Harbor Industrial',
    'Island Circuits', 'Jetstream Parts', 'Keystone Hydraulics', 'Luna Optics',
]
countries = ['USA', 'Mexico', 'Puerto Rico', 'Germany', 'China', 'Costa Rica']

suppliers = pd.DataFrame({
    'supplier_id': [f'S{i:03d}' for i in range(1, 13)],
    'supplier_name': names,
    'country': [random.choice(countries) for _ in names],
    'lead_time_days': [random.randint(5, 45) for _ in names],
})

late_bias = {s: random.choice([0, 0, 1, 3, 6]) for s in suppliers.supplier_id}
short_rate = {s: random.choice([0.02, 0.03, 0.05, 0.15, 0.25]) for s in suppliers.supplier_id}

parts = [
    {
        'part_id': f'P{i:04d}',
        'category': random.choice(['Electronics', 'Fasteners', 'Cables', 'Hydraulics', 'Plastics']),
        'base_price': round(random.uniform(2, 400), 2),
    }
    for i in range(1, 101)
]

sup_records = suppliers.to_dict('records')
pos, receipts = [], []
start = date(2025, 1, 1)

for i in range(1, N_PO + 1):
    s = random.choice(sup_records)
    p = random.choice(parts)
    qty = random.choice([10, 25, 50, 100, 250, 500])
    order = start + timedelta(days=random.randint(0, 364))
    promised = order + timedelta(days=s['lead_time_days'])

    # Inject messy supplier names (case, trailing space, typo)
    name = s['supplier_name']
    r = random.random()
    if r < 0.03:
        name = name.upper()
    elif r < 0.06:
        name = name + ' '
    elif r < 0.08:
        name = name[:-1]

    po_id = f'PO{i:05d}'
    pos.append({
        'po_id': po_id,
        'supplier_id': s['supplier_id'],
        'supplier_name': name,
        'part_id': p['part_id'],
        'category': p['category'],
        'qty_ordered': qty,
        'unit_cost': round(p['base_price'] * random.uniform(0.95, 1.15), 2),
        'order_date': order,
        'promised_date': promised,
    })

    if random.random() < 0.03:
        continue  # order not received yet

    delay = random.randint(-2, 3) + late_bias[s['supplier_id']]
    if random.random() < 0.1:
        delay += random.randint(0, 10)

    got = qty if random.random() > short_rate[s['supplier_id']] else int(qty * random.uniform(0.5, 0.95))
    receipts.append({
        'po_id': po_id,
        'qty_received': got,
        'received_date': promised + timedelta(days=delay),
    })

po_df = pd.DataFrame(pos)
po_df = pd.concat([po_df, po_df.sample(50, random_state=1)])  # 50 duplicate rows

rc_df = pd.DataFrame(receipts)
rc_df.loc[rc_df.sample(60, random_state=2).index, 'received_date'] = None  # blank dates

suppliers.to_csv('data/raw/suppliers.csv', index=False)
po_df.to_csv('data/raw/purchase_orders.csv', index=False)
rc_df.to_csv('data/raw/receipts.csv', index=False)

print('Done:', len(po_df), 'PO rows,', len(rc_df), 'receipt rows')
