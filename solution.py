from flask import Flask, request, jsonify
import math
from collections import defaultdict
import itertools

app = Flask(__name__)

# --- Global Data ---

edges = {
    ("C1", "C2"): 4, ("C2", "C3"): 3,
    ("C1", "S"): 3, ("C2", "S"): 2.5, ("C3", "S"): 2,
}

center_stock = {
    "C1": {"A", "B", "C"},
    "C2": {"D", "E", "F"},
    "C3": {"G", "H", "I"},
}

product_weights = {
    "A": 3, "B": 2, "C": 8,
    "D": 12, "E": 25, "F": 15,
    "G": 0.5, "H": 1, "I": 2,
}

# --- Helper Functions ---

def cost(weight):
    if weight <= 5:
        return 10
    return 10 + math.ceil((weight - 5) / 5) * 8

def get_distance(a, b):
    if (a, b) in edges: return edges[(a, b)]
    if (b, a) in edges: return edges[(b, a)]
    return float('inf')

def compute_weights_per_center(order):
    cw = defaultdict(float)
    for p, qty in order.items():
        w = product_weights[p] * qty
        for center, items in center_stock.items():
            if p in items:
                cw[center] += w
                break
    return dict(cw)

def a_b(x, a, b):
    wt1 = center_weights[a]
    wt2 = center_weights[b]
    n1 = get_distance(a, b) * cost(x + wt1) + get_distance(b, "S") * cost(x + wt1 + wt2)
    n2 = get_distance(a, "S") * cost(x + wt1) + get_distance("S", b) * cost(0) + get_distance(b, "S") * cost(wt2)
    return min(n1, n2)

def compute_cost_if_one_center(wdict):
    c, w = next(iter(wdict.items()))
    return get_distance(c, "S") * cost(w)

def compute_cost_if_two_centers():
    c1, c2 = center_weights.keys()
    return min(a_b(0, c1, c2), a_b(0, c2, c1))

def compute_cost_if_three_centers():
    best = float('inf')
    for k1, k2, k3 in itertools.permutations(center_weights):
        w1 = center_weights[k1]
        n1 = get_distance(k1, "S") * cost(w1) + get_distance("S", k2) * cost(0) + a_b(0, k2, k3)
        n2 = get_distance(k1, k2) * cost(w1) + a_b(w1, k2, k3)
        best = min(best, n1, n2)
    return best

def calculate_cost(order):
    global center_weights
    center_weights = compute_weights_per_center(order)

    # print(center_weights)

    cnt = len(center_weights)
    
    if cnt == 1:
        total_cost = compute_cost_if_one_center(center_weights)
    elif cnt == 2:
        total_cost = compute_cost_if_two_centers()
    elif cnt == 3:
        total_cost = compute_cost_if_three_centers()
    else:
        return None

    if total_cost == int(total_cost):
        return int(total_cost)
    else:
        return total_cost

# --- API Route ---

@app.route('/', methods=['POST'])
def deliver_cost():
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400
    order = request.get_json()
    print(order)
    print("----------------------------------")
    total = calculate_cost(order)
    return jsonify({"total_cost": round(total)})

if __name__ == '__main__':
    app.run(debug=True)


# order = {"A": 1, "G": 1, "H": 1, "I":3}
# order = {"A": 1, "B": 1, "C": 1, "D": 1}
# order = {'A': 1, 'B': 2, 'C': 1, 'D': 5, 'E': 1, 'F': 1, 'G': 2, 'H': 1, 'I': 1}
# print(calculate_cost(order))



















