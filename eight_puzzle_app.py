import copy
import heapq
import math
import random
import threading
import time
import tkinter as tk
from collections import deque
from tkinter import messagebox, ttk

# ==========================================
# CẤU HÌNH & HẰNG SỐ BÀI TOÁN
# ==========================================
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
SUCCESS = "SUCCESS"
FAILURE = "FAILURE"


# 1. Hàm tính khoảng cách Manhattan (Heuristic h)
def tinh_h(state, goal=None):
    if goal is None:
        goal = GOAL
    khoang_cach = 0
    for i in range(9):
        tile = state[i]
        if tile != 0:
            # Vị trí hiện tại (dòng, cột)
            r_hien_tai, c_hien_tai = divmod(i, 3)
            # Vị trí đích (dòng, cột)
            idx_dich = goal.index(tile)
            r_dich, c_dich = divmod(idx_dich, 3)
            khoang_cach += abs(r_hien_tai - r_dich) + abs(c_hien_tai - c_dich)
    return khoang_cach


# 2. Hàm tìm các trạng thái kề (di chuyển ô trống)
def lay_cac_trang_thai_ke(state):
    ke = []
    idx = state.index(0)  # Tìm vị trí ô trống
    r, c = divmod(idx, 3)

    # Các hướng di chuyển: Lên, Xuống, Trái, Phải
    huong = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in huong:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            moi_idx = nr * 3 + nc
            moi_state = list(state)
            # Hoán đổi ô trống với ô số
            moi_state[idx], moi_state[moi_idx] = moi_state[moi_idx], moi_state[idx]
            ke.append(tuple(moi_state))
    return ke


def dem_nghich_the_theo_dich(state, goal):
    thu_tu_dich = {tile: idx for idx, tile in enumerate(goal) if tile != 0}
    day = [thu_tu_dich[tile] for tile in state if tile != 0]
    nghich_the = 0
    for i in range(len(day)):
        for j in range(i + 1, len(day)):
            if day[i] > day[j]:
                nghich_the += 1
    return nghich_the


def co_the_giai(start, goal):
    # Với bảng 3x3, hai trạng thái cùng khả năng giải khi parity nghịch thế giống nhau.
    return dem_nghich_the_theo_dich(start, goal) % 2 == 0


def tao_parent_map(path):
    if not path:
        return {}
    parent_map = {path[0]: None}
    for i in range(1, len(path)):
        parent_map[path[i]] = path[i - 1]
    return parent_map


def tim_duong_di_hai_chieu(start, goal, max_nodes=200000):
    if start == goal:
        return [start]

    q_start = deque([start])
    q_goal = deque([goal])
    parent_start = {start: None}
    parent_goal = {goal: None}

    def mo_rong(queue, own_parent, other_parent):
        for _ in range(len(queue)):
            state = queue.popleft()
            for neighbor in lay_cac_trang_thai_ke(state):
                if neighbor in own_parent:
                    continue
                own_parent[neighbor] = state
                if neighbor in other_parent:
                    return neighbor
                queue.append(neighbor)
        return None

    while q_start and q_goal and len(parent_start) + len(parent_goal) <= max_nodes:
        if len(q_start) <= len(q_goal):
            meet = mo_rong(q_start, parent_start, parent_goal)
        else:
            meet = mo_rong(q_goal, parent_goal, parent_start)

        if meet is not None:
            left = []
            curr = meet
            while curr is not None:
                left.append(curr)
                curr = parent_start[curr]
            left.reverse()

            right = []
            curr = parent_goal[meet]
            while curr is not None:
                right.append(curr)
                curr = parent_goal[curr]
            return left + right

    return None


# ==========================================
# CÁC THUẬT TOÁN TÌM KIẾM
# ==========================================

# 1. THUẬT TOÁN A*
def A_Star(Start, goal=None):
    if goal is None:
        goal = GOAL
    FRONTIER = [Start]
    REACHED = []
    g = {Start: 0}
    f = {Start: tinh_h(Start, goal)}
    dinh_cha = {Start: None}

    trace = []

    while FRONTIER:
        # Chọn n có f nhỏ nhất
        n = min(FRONTIER, key=lambda x: f[x])

        if n == goal:
            trace.append({
                'node': n,
                'frontier': list(FRONTIER),
                'explored': list(REACHED),
                'f': dict(f)
            })
            return "Thành công", dinh_cha, trace

        FRONTIER.remove(n)
        REACHED.append(n)

        for m in lay_cac_trang_thai_ke(n):
            g_new = g[n] + 1  # cost mỗi bước là 1

            if m in REACHED:
                if g_new >= g[m]:
                    continue
                REACHED.remove(m)
                g[m] = g_new
                f[m] = g[m] + tinh_h(m, goal)
                dinh_cha[m] = n
                FRONTIER.append(m)
            elif m in FRONTIER:
                if g_new < g[m]:
                    g[m] = g_new
                    f[m] = g[m] + tinh_h(m, goal)
                    dinh_cha[m] = n
            else:
                g[m] = g_new
                f[m] = g[m] + tinh_h(m, goal)
                dinh_cha[m] = n
                FRONTIER.append(m)

        # Ghi nhận sau khi duyệt xong các trạng thái kề
        trace.append({
            'node': n,
            'frontier': list(FRONTIER),
            'explored': list(REACHED),
            'f': dict(f)
        })

    return "Thất bại", None, trace


# 2. THUẬT TOÁN GREEDY
def Greedy_Search(Start, goal=None):
    if goal is None:
        goal = GOAL
    FRONTIER = [Start]
    REACHED = []
    dinh_cha = {Start: None}

    trace = []

    while FRONTIER:
        # Chọn n có h nhỏ nhất
        n = min(FRONTIER, key=lambda x: tinh_h(x, goal))

        if n == goal:
            trace.append({
                'node': n,
                'frontier': list(FRONTIER),
                'explored': list(REACHED),
                'h': {x: tinh_h(x, goal) for x in FRONTIER + REACHED + [n]}
            })
            return "Thành công", dinh_cha, trace

        FRONTIER.remove(n)
        REACHED.append(n)

        for m in lay_cac_trang_thai_ke(n):
            if (m not in FRONTIER) and (m not in REACHED):
                dinh_cha[m] = n
                FRONTIER.append(m)

        trace.append({
            'node': n,
            'frontier': list(FRONTIER),
            'explored': list(REACHED),
            'h': {x: tinh_h(x, goal) for x in FRONTIER + REACHED}
        })

    return "Thất bại", None, trace


# 3. THUẬT TOÁN BFS
def BFS(Start, goal=None):
    if goal is None:
        goal = GOAL

    FRONTIER = deque([Start])
    frontier_set = {Start}
    REACHED = []
    reached_set = set()
    dinh_cha = {Start: None}
    trace = []

    while FRONTIER:
        n = FRONTIER.popleft()
        frontier_set.remove(n)

        trace.append({
            'node': n,
            'frontier': list(FRONTIER),
            'explored': list(REACHED)
        })

        if n == goal:
            return SUCCESS, dinh_cha, trace

        REACHED.append(n)
        reached_set.add(n)

        for m in lay_cac_trang_thai_ke(n):
            if m not in frontier_set and m not in reached_set:
                dinh_cha[m] = n
                FRONTIER.append(m)
                frontier_set.add(m)

    return FAILURE, None, trace


# 4. THUẬT TOÁN DFS
def DFS(Start, goal=None):
    if goal is None:
        goal = GOAL

    FRONTIER = [Start]
    frontier_set = {Start}
    REACHED = []
    reached_set = set()
    dinh_cha = {Start: None}
    trace = []

    while FRONTIER:
        n = FRONTIER.pop()
        frontier_set.remove(n)

        trace.append({
            'node': n,
            'frontier': list(FRONTIER),
            'explored': list(REACHED)
        })

        if n == goal:
            return SUCCESS, dinh_cha, trace

        REACHED.append(n)
        reached_set.add(n)

        for m in lay_cac_trang_thai_ke(n):
            if m not in frontier_set and m not in reached_set:
                dinh_cha[m] = n
                FRONTIER.append(m)
                frontier_set.add(m)

    return FAILURE, None, trace


# 5. THUẬT TOÁN IDS
def IDS(Start, goal=None, max_depth=50):
    if goal is None:
        goal = GOAL

    trace = []

    for limit in range(max_depth + 1):
        FRONTIER = [(Start, 0)]
        dinh_cha = {Start: None}
        REACHED = []

        while FRONTIER:
            n, depth = FRONTIER.pop()
            trace.append({
                'node': n,
                'frontier': [state for state, _ in FRONTIER],
                'explored': list(REACHED),
                'depth': depth,
                'limit': limit
            })

            if n == goal:
                return SUCCESS, dinh_cha, trace

            REACHED.append(n)

            if depth < limit:
                path_seen = set()
                curr = n
                while curr is not None:
                    path_seen.add(curr)
                    curr = dinh_cha[curr]

                for m in reversed(lay_cac_trang_thai_ke(n)):
                    if m not in path_seen:
                        dinh_cha[m] = n
                        FRONTIER.append((m, depth + 1))

    return FAILURE, None, trace


# 6. THUẬT TOÁN UCS
def UCS(Start, goal=None):
    if goal is None:
        goal = GOAL

    counter = 0
    FRONTIER = [(0, counter, Start)]
    frontier_cost = {Start: 0}
    REACHED = []
    reached_set = set()
    g = {Start: 0}
    dinh_cha = {Start: None}
    trace = []

    while FRONTIER:
        cost, _, n = heapq.heappop(FRONTIER)
        if cost != frontier_cost.get(n):
            continue

        del frontier_cost[n]

        trace.append({
            'node': n,
            'frontier': [state for _, _, state in FRONTIER if state in frontier_cost],
            'explored': list(REACHED),
            'g': dict(g)
        })

        if n == goal:
            return SUCCESS, dinh_cha, trace

        REACHED.append(n)
        reached_set.add(n)

        for m in lay_cac_trang_thai_ke(n):
            g_new = cost + 1
            if m in reached_set and g_new >= g[m]:
                continue

            if g_new < g.get(m, float('inf')):
                g[m] = g_new
                dinh_cha[m] = n
                counter += 1
                heapq.heappush(FRONTIER, (g_new, counter, m))
                frontier_cost[m] = g_new

    return FAILURE, None, trace


# 7. THUẬT TOÁN HILL CLIMBING (LOCAL SEARCH)
def Local_Search(Start, goal=None, max_steps=1000):
    if goal is None:
        goal = GOAL

    current = Start
    dinh_cha = {Start: None}
    REACHED = []
    trace = []

    for _ in range(max_steps):
        neighbors = [m for m in lay_cac_trang_thai_ke(current) if m not in REACHED]
        h_values = {x: tinh_h(x, goal) for x in neighbors + REACHED + [current]}

        trace.append({
            'node': current,
            'frontier': list(neighbors),
            'explored': list(REACHED),
            'h': h_values
        })

        if current == goal:
            return "Thành công", dinh_cha, trace

        if not neighbors:
            return "Thất bại", None, trace

        best_neighbor = min(neighbors, key=lambda x: tinh_h(x, goal))

        # Hill climbing chỉ di chuyển khi trạng thái kề tốt hơn trạng thái hiện tại.
        if tinh_h(best_neighbor, goal) >= tinh_h(current, goal):
            return "Thất bại", None, trace

        REACHED.append(current)
        dinh_cha[best_neighbor] = current
        current = best_neighbor

    return "Thất bại", None, trace


# 8. THUẬT TOÁN STOCHASTIC HILL CLIMBING
def Stochastic_Hill_Climbing(Start, goal=None, max_steps=1000):
    if goal is None:
        goal = GOAL

    current = Start
    dinh_cha = {Start: None}
    REACHED = []
    trace = []

    for _ in range(max_steps):
        neighbors = [m for m in lay_cac_trang_thai_ke(current) if m not in REACHED]
        h_values = {x: tinh_h(x, goal) for x in neighbors + REACHED + [current]}

        trace.append({
            'node': current,
            'frontier': list(neighbors),
            'explored': list(REACHED),
            'h': h_values
        })

        if current == goal:
            return SUCCESS, dinh_cha, trace

        current_h = tinh_h(current, goal)
        better_neighbors = [m for m in neighbors if tinh_h(m, goal) < current_h]

        if not better_neighbors:
            return FAILURE, None, trace

        next_state = random.choice(better_neighbors)
        REACHED.append(current)
        dinh_cha[next_state] = current
        current = next_state

    return FAILURE, None, trace


# 9. THUẬT TOÁN LOCAL BEAM SEARCH
def Local_Beam_Search(Start, goal=None, beam_width=3, max_steps=1000):
    if goal is None:
        goal = GOAL

    FRONTIER = [Start]
    REACHED = []
    reached_set = set()
    dinh_cha = {Start: None}
    trace = []

    for _ in range(max_steps):
        current = min(FRONTIER, key=lambda x: tinh_h(x, goal))
        h_values = {x: tinh_h(x, goal) for x in FRONTIER + REACHED}

        trace.append({
            'node': current,
            'frontier': list(FRONTIER),
            'explored': list(REACHED),
            'h': h_values
        })

        if current == goal:
            return SUCCESS, dinh_cha, trace

        candidates = []
        for n in FRONTIER:
            if n not in reached_set:
                REACHED.append(n)
                reached_set.add(n)

            for m in lay_cac_trang_thai_ke(n):
                if m in reached_set:
                    continue
                if m not in dinh_cha:
                    dinh_cha[m] = n
                candidates.append(m)

        if not candidates:
            return FAILURE, None, trace

        unique_candidates = list(dict.fromkeys(candidates))
        unique_candidates.sort(key=lambda x: tinh_h(x, goal))
        FRONTIER = unique_candidates[:beam_width]

    return FAILURE, None, trace


# 10. THUẬT TOÁN SIMULATED ANNEALING
def Simulated_Annealing(Start, goal=None, T0=20.0, Tmin=0.001, alpha=0.99):
    if goal is None:
        goal = GOAL

    current_state = Start
    T = T0
    REACHED = []
    trace = []

    # Lưu vết các trạng thái thực tế đã đi qua
    visited_states = [Start]

    while T > Tmin:
        neighbors = lay_cac_trang_thai_ke(current_state)
        h_values = {x: tinh_h(x, goal) for x in neighbors + REACHED + [current_state]}

        trace.append({
            'node': current_state,
            'frontier': list(neighbors),
            'explored': list(REACHED),
            'h': h_values,
            'T': T
        })

        if current_state == goal:
            # Khử chu kỳ trong visited_states để tạo parent map sạch
            pruned = []
            last_occ = {}
            for i, st in enumerate(visited_states):
                last_occ[st] = i
            i = 0
            while i < len(visited_states):
                pruned.append(visited_states[i])
                i = last_occ[visited_states[i]] + 1

            dinh_cha = {pruned[0]: None}
            for idx in range(1, len(pruned)):
                dinh_cha[pruned[idx]] = pruned[idx - 1]

            return "Thành công", dinh_cha, trace

        if not neighbors:
            break

        next_state = random.choice(neighbors)
        delta = tinh_h(next_state, goal) - tinh_h(current_state, goal)

        if current_state not in REACHED:
            REACHED.append(current_state)

        if delta < 0:
            current_state = next_state
            visited_states.append(current_state)
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current_state = next_state
                visited_states.append(current_state)

        T = alpha * T

    # Ghi nhận trạng thái cuối cùng
    neighbors = lay_cac_trang_thai_ke(current_state)
    h_values = {x: tinh_h(x, goal) for x in neighbors + REACHED + [current_state]}
    trace.append({
        'node': current_state,
        'frontier': list(neighbors),
        'explored': list(REACHED),
        'h': h_values,
        'T': T
    })

    if current_state == goal:
        pruned = []
        last_occ = {}
        for i, st in enumerate(visited_states):
            last_occ[st] = i
        i = 0
        while i < len(visited_states):
            pruned.append(visited_states[i])
            i = last_occ[visited_states[i]] + 1

        dinh_cha = {pruned[0]: None}
        for idx in range(1, len(pruned)):
            dinh_cha[pruned[idx]] = pruned[idx - 1]

        return "Thành công", dinh_cha, trace
    else:
        return "Thất bại", None, trace


# ==========================================
# CÁC HÀM TRỢ GIÚP GIAO DIỆN ĐỒ HỌA
# ==========================================
# 11. THUAT TOAN AND-OR GRAPH SEARCH
def And_Or_Graph_Search(Start, goal=None, max_depth=50, max_nodes=50000):
    if goal is None:
        goal = GOAL

    trace = []

    def actions(state):
        neighbors = lay_cac_trang_thai_ke(state)
        neighbors.sort(key=lambda x: tinh_h(x, goal))
        return neighbors

    def results(state, action):
        # Bai toan 8-puzzle la tat dinh: moi action chi sinh ra 1 state ket qua.
        return [action]

    def or_search(state, path):
        neighbor_actions = actions(state)
        trace.append({
            'node': state,
            'frontier': list(neighbor_actions),
            'explored': list(path),
            'h': {x: tinh_h(x, goal) for x in neighbor_actions + list(path) + [state]},
            'depth': len(path)
        })

        if state == goal:
            return []

        if state in path or len(path) >= max_depth or len(trace) >= max_nodes:
            return FAILURE

        for action in neighbor_actions:
            result_states = results(state, action)
            plan = and_search(result_states, path + [state])
            if plan != FAILURE:
                return [action, plan]

        return FAILURE

    def and_search(states, path):
        plans = {}
        for state in states:
            plan_s = or_search(state, path)
            if plan_s == FAILURE:
                return FAILURE
            plans[state] = plan_s
        return plans

    def plan_to_parent_map(start, plan):
        parent_map = {start: None}
        current = start
        current_plan = plan

        while current_plan:
            action, branch_plans = current_plan
            next_state = action
            parent_map[next_state] = current
            current = next_state
            current_plan = branch_plans.get(next_state, [])

        return parent_map

    plan = or_search(Start, [])
    if plan == FAILURE:
        return FAILURE, None, trace

    parent_map = plan_to_parent_map(Start, plan)
    return SUCCESS, parent_map, trace


# ==========================================
# CÁC THUẬT TOÁN CSP (CONSTRAINT SATISFACTION PROBLEM)
# ==========================================

# 1. CSP BACKTRACKING
def CSP_Backtracking(Start, goal=None):
    if goal is None:
        goal = GOAL
    max_d = 22
    min_d = tinh_h(Start, goal)
    
    trace = []
    
    for d in range(min_d, max_d + 1):
        if (d - min_d) % 2 != 0:
            continue
        path = [Start]
        
        def backtrack(step_idx):
            current = path[-1]
            neighbors = [m for m in lay_cac_trang_thai_ke(current) if m not in path]
            
            trace.append({
                'node': current,
                'frontier': neighbors,
                'explored': list(path),
                'csp': f"d={d}, step={step_idx}"
            })
            
            if len(trace) >= 5000:
                return False
            
            if step_idx == d:
                return current == goal
                
            for neighbor in neighbors:
                path.append(neighbor)
                if backtrack(step_idx + 1):
                    return True
                path.pop()
            return False

        if backtrack(0):
            parent_map = {}
            for i in range(1, len(path)):
                parent_map[path[i]] = path[i-1]
            parent_map[Start] = None
            return SUCCESS, parent_map, trace
            
    return FAILURE, None, trace


# 2. CSP FORWARD CHECKING
def CSP_Forward_Checking(Start, goal=None):
    if goal is None:
        goal = GOAL
    max_d = 22
    min_d = tinh_h(Start, goal)
    
    trace = []
    
    for d in range(min_d, max_d + 1):
        if (d - min_d) % 2 != 0:
            continue
        path = [Start]
        
        def backtrack(step_idx):
            current = path[-1]
            neighbors = [m for m in lay_cac_trang_thai_ke(current) if m not in path]
            
            # Forward checking sử dụng heuristic pruning (loại bỏ các hướng đi không thể chạm đích)
            filtered_neighbors = []
            pruned_count = 0
            for neighbor in neighbors:
                if tinh_h(neighbor, goal) <= d - (step_idx + 1):
                    filtered_neighbors.append(neighbor)
                else:
                    pruned_count += 1
                    
            trace.append({
                'node': current,
                'frontier': filtered_neighbors,
                'explored': list(path),
                'csp': f"d={d}, step={step_idx}, pruned={pruned_count}"
            })
            
            if len(trace) >= 5000:
                return False
                
            if step_idx == d:
                return current == goal
                
            if not filtered_neighbors:
                return False
                
            for neighbor in filtered_neighbors:
                path.append(neighbor)
                if backtrack(step_idx + 1):
                    return True
                path.pop()
            return False

        if backtrack(0):
            parent_map = {}
            for i in range(1, len(path)):
                parent_map[path[i]] = path[i-1]
            parent_map[Start] = None
            return SUCCESS, parent_map, trace
            
    return FAILURE, None, trace


# 3. CSP AC-3
def CSP_AC3(Start, goal=None):
    if goal is None:
        goal = GOAL

    trace = []

    if not co_the_giai(Start, goal):
        trace.append({
            'node': Start,
            'frontier': [],
            'explored': [],
            'csp': "AC-3: trang thai khong cung parity voi dich"
        })
        return FAILURE, None, trace

    duong_di_ngan_nhat = tim_duong_di_hai_chieu(Start, goal)
    if not duong_di_ngan_nhat:
        trace.append({
            'node': Start,
            'frontier': [],
            'explored': [],
            'csp': "AC-3: vuot gioi han mo rong"
        })
        return FAILURE, None, trace

    d = len(duong_di_ngan_nhat) - 1
    neighbor_cache = {}

    def neighbors(state):
        if state not in neighbor_cache:
            neighbor_cache[state] = set(lay_cac_trang_thai_ke(state))
        return neighbor_cache[state]

    forward_layers = {0: {Start}}
    for i in range(1, d + 1):
        curr_layer = set()
        for st in forward_layers[i - 1]:
            curr_layer.update(neighbors(st))
        forward_layers[i] = {st for st in curr_layer if tinh_h(st, goal) <= d - i}

    backward_layers = {0: {goal}}
    for j in range(1, d + 1):
        curr_layer = set()
        for st in backward_layers[j - 1]:
            curr_layer.update(neighbors(st))
        backward_layers[j] = {st for st in curr_layer if tinh_h(st, Start) <= d - j}

    D = {
        i: forward_layers[i].intersection(backward_layers[d - i])
        for i in range(d + 1)
    }
    D[0] = {Start}
    D[d] = {goal}

    if any(len(D[i]) == 0 for i in range(d + 1)):
        parent_map = tao_parent_map(duong_di_ngan_nhat)
        trace.append({
            'node': Start,
            'frontier': duong_di_ngan_nhat[1:2],
            'explored': duong_di_ngan_nhat,
            'csp': f"AC-3 fallback: duong di ngan nhat {d} buoc"
        })
        return SUCCESS, parent_map, trace

    queue = deque()
    for i in range(d):
        queue.append((i, i + 1))
        queue.append((i + 1, i))

    def revise(i, j):
        to_remove = {x for x in D[i] if neighbors(x).isdisjoint(D[j])}
        if not to_remove:
            return False
        D[i] -= to_remove
        return True

    possible = True
    while queue:
        i, j = queue.popleft()
        if revise(i, j):
            if not D[i]:
                possible = False
                break
            for neighbor_idx in (i - 1, i + 1):
                if 0 <= neighbor_idx <= d and neighbor_idx != j:
                    queue.append((neighbor_idx, i))

    if not possible:
        parent_map = tao_parent_map(duong_di_ngan_nhat)
        trace.append({
            'node': Start,
            'frontier': duong_di_ngan_nhat[1:2],
            'explored': duong_di_ngan_nhat,
            'csp': f"AC-3 fallback: mien rong, dung duong di ngan nhat {d} buoc"
        })
        return SUCCESS, parent_map, trace

    path = [Start]
    max_trace = 800

    def backtrack(step_idx):
        current = path[-1]
        if step_idx == d:
            return current == goal

        next_domain = [
            m for m in neighbors(current)
            if m in D[step_idx + 1] and m not in path
        ]
        next_domain.sort(key=lambda st: (tinh_h(st, goal), st))

        if len(trace) < max_trace:
            trace.append({
                'node': current,
                'frontier': next_domain,
                'explored': list(path),
                'csp': f"AC-3 d={d}, step={step_idx}, dom_sizes={[len(D[k]) for k in range(d + 1)]}"
            })

        for neighbor in next_domain:
            path.append(neighbor)
            if backtrack(step_idx + 1):
                return True
            path.pop()
        return False

    if backtrack(0):
        return SUCCESS, tao_parent_map(path), trace

    parent_map = tao_parent_map(duong_di_ngan_nhat)
    trace.append({
        'node': duong_di_ngan_nhat[-1],
        'frontier': [],
        'explored': duong_di_ngan_nhat,
        'csp': f"AC-3 fallback: backtracking khong tim duoc nhanh, dung path {d} buoc"
    })
    return SUCCESS, parent_map, trace

    return FAILURE, None, trace


# 4. CSP MIN-CONFLICTS
def CSP_Min_Conflicts(Start, goal=None):
    if goal is None:
        goal = GOAL
    max_d = 22
    min_d = tinh_h(Start, goal)
    
    trace = []
    max_steps = 300
    
    for d in range(min_d, max_d + 1):
        if (d - min_d) % 2 != 0:
            continue
            
        # Khởi tạo chuỗi trạng thái từ Start đến Goal bằng Random Walk từ hai đầu
        path = [Start] * (d + 1)
        path[0] = Start
        path[d] = goal
        
        curr = Start
        for i in range(1, d // 2):
            ke = lay_cac_trang_thai_ke(curr)
            curr = random.choice(ke) if ke else curr
            path[i] = curr
            
        curr = goal
        for i in range(d - 1, d // 2 - 1, -1):
            ke = lay_cac_trang_thai_ke(curr)
            curr = random.choice(ke) if ke else curr
            path[i] = curr

        def get_conflicts(p):
            conflicts = 0
            for i in range(d):
                if p[i+1] not in lay_cac_trang_thai_ke(p[i]):
                    conflicts += 1
            # Thêm hình phạt chu kỳ trùng lặp để giảm thiểu lặp lại trạng thái
            seen = set()
            for st in p:
                if st in seen:
                    conflicts += 1
                seen.add(st)
            return conflicts

        for step in range(max_steps):
            current_conflicts = get_conflicts(path)
            
            trace.append({
                'node': path[d // 2],
                'frontier': list(path),
                'explored': [],
                'csp': f"MC d={d}, step={step}, conflicts={current_conflicts}"
            })
            
            if len(trace) >= 5000:
                return FAILURE, None, trace
                
            if current_conflicts == 0:
                parent_map = {}
                for i in range(1, len(path)):
                    parent_map[path[i]] = path[i-1]
                parent_map[Start] = None
                return SUCCESS, parent_map, trace
                
            # Tìm các biến có xung đột
            conflict_vars = []
            for i in range(1, d):
                is_conflict = (path[i] not in lay_cac_trang_thai_ke(path[i-1])) or \
                              (path[i+1] not in lay_cac_trang_thai_ke(path[i])) or \
                              (path.count(path[i]) > 1)
                if is_conflict:
                    conflict_vars.append(i)
                    
            if not conflict_vars:
                conflict_vars = list(range(1, d))
                
            var_idx = random.choice(conflict_vars)
            candidates = set(lay_cac_trang_thai_ke(path[var_idx - 1])).union(lay_cac_trang_thai_ke(path[var_idx + 1]))
            
            best_val = path[var_idx]
            min_c = current_conflicts
            best_candidates = [best_val]
            
            for val in candidates:
                old_val = path[var_idx]
                path[var_idx] = val
                c = get_conflicts(path)
                path[var_idx] = old_val
                
                if c < min_c:
                    min_c = c
                    best_candidates = [val]
                elif c == min_c:
                    best_candidates.append(val)
                    
            path[var_idx] = random.choice(best_candidates)
            
    return FAILURE, None, trace


def format_state_list(states):
    if not states:
        return "", "", ""

    def to_char(x):
        return "_" if x == 0 else str(x)

    row0 = " | ".join(f"{to_char(s[0])} {to_char(s[1])} {to_char(s[2])}" for s in states)
    row1 = " | ".join(f"{to_char(s[3])} {to_char(s[4])} {to_char(s[5])}" for s in states)
    row2 = " | ".join(f"{to_char(s[6])} {to_char(s[7])} {to_char(s[8])}" for s in states)
    return row0, row1, row2


def state_to_text(state):
    return " ".join("_" if x == 0 else str(x) for x in state)


def parse_puzzle_state(text):
    parts = text.replace(",", " ").replace("_", "0").split()
    state = tuple(int(x) for x in parts)
    if len(state) != 9 or set(state) != set(range(9)):
        raise ValueError
    return state


# ==========================================
# LỚP GIAO DIỆN CHÍNH (GUI CLASS)
# ==========================================
class EightPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Search Dashboard")
        self.root.geometry("1320x760")
        self.root.minsize(1100, 680)

        self.algorithms = {
            "A*": A_Star,
            "Greedy": Greedy_Search,
            "Local Search": Local_Search,
            "Local Beam": Local_Beam_Search,
            "Stochastic HC": Stochastic_Hill_Climbing,
            "Simulated Annealing": Simulated_Annealing,
            "AND-OR Search": And_Or_Graph_Search,
            "BFS": BFS,
            "DFS": DFS,
            "IDS": IDS,
            "UCS": UCS,
            "CSP Backtracking": CSP_Backtracking,
            "CSP Forward Checking": CSP_Forward_Checking,
            "CSP AC-3": CSP_AC3,
            "CSP Min-Conflicts": CSP_Min_Conflicts,
        }

        self.state = list(GOAL)
        self.buttons = []
        self.path = []
        self.current_step = 0
        self.playback_job = None
        self.is_playing = False
        self.playback_delay_ms = 600
        self.is_solving = False

        self.configure_style()
        self.create_widgets()
        self.update_grid(self.state)

    def configure_style(self):
        self.root.configure(bg="#eef2f7")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#eef2f7")
        style.configure("Panel.TFrame", background="#ffffff", relief=tk.FLAT)
        style.configure("Header.TLabel", background="#eef2f7", foreground="#172033", font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background="#ffffff", foreground="#172033", font=("Segoe UI", 11, "bold"))
        style.configure("Info.TLabel", background="#ffffff", foreground="#475569", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#ffffff", foreground="#2563eb", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe", background="#ffffff", bordercolor="#cbd5e1", relief=tk.SOLID)
        style.configure("TLabelframe.Label", background="#ffffff", foreground="#172033", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 7))
        style.configure("Treeview", font=("Consolas", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def create_widgets(self):
        header = ttk.Frame(self.root, padding=(18, 14, 18, 8))
        header.pack(fill=tk.X)
        ttk.Label(header, text="8-Puzzle Search Dashboard", style="Header.TLabel").pack(side=tk.LEFT)

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))

        left_frame = ttk.Frame(main, style="Panel.TFrame", padding=14, width=360)
        right_frame = ttk.Frame(main, style="Panel.TFrame", padding=12)
        left_frame.pack_propagate(False)
        main.add(left_frame, weight=0)
        main.add(right_frame, weight=4)

        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent):
        ttk.Label(parent, text="Bàn cờ", style="SubHeader.TLabel").pack(anchor=tk.W)

        grid_frame = tk.Frame(parent, bg="#334155", bd=0, padx=4, pady=4)
        grid_frame.pack(pady=(6, 10))

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Segoe UI", 18, "bold"),
                width=3,
                height=1,
                relief=tk.FLAT,
                command=lambda idx=i: self.move_tile(idx),
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="nsew")
            self.buttons.append(btn)

        info_frame = ttk.Frame(parent, style="Panel.TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 8))
        self.lbl_current = ttk.Label(info_frame, text="", style="Info.TLabel")
        self.lbl_current.pack(anchor=tk.W)
        self.lbl_status = ttk.Label(
            info_frame,
            text="Sẵn sàng. Chọn thuật toán để giải hoặc tự di chuyển ô.",
            style="Status.TLabel",
            wraplength=330,
        )
        self.lbl_status.pack(anchor=tk.W, pady=(4, 0))

        start_frame = ttk.LabelFrame(parent, text="Trạng thái bắt đầu", padding=6)
        start_frame.pack(fill=tk.X, pady=(0, 8))
        self.entry_start = ttk.Entry(start_frame, font=("Consolas", 11))
        self.entry_start.insert(0, state_to_text(self.state))
        self.entry_start.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(start_frame, text="Áp dụng", command=self.apply_start_state).grid(row=0, column=1, sticky="ew")
        start_frame.columnconfigure(0, weight=3)
        start_frame.columnconfigure(1, weight=1)

        goal_frame = ttk.LabelFrame(parent, text="Trạng thái đích", padding=6)
        goal_frame.pack(fill=tk.X, pady=(0, 8))
        self.entry_goal = ttk.Entry(goal_frame, font=("Consolas", 11))
        self.entry_goal.insert(0, "1 2 3 4 5 6 7 8 0")
        self.entry_goal.pack(fill=tk.X)

        control_frame = ttk.LabelFrame(parent, text="Điều khiển", padding=6)
        control_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(control_frame, text="Xáo trộn", command=self.shuffle, style="Accent.TButton").grid(
            row=0, column=0, sticky="ew", padx=3, pady=3
        )
        ttk.Button(control_frame, text="Xóa trace", command=self.clear_solution).grid(
            row=0, column=1, sticky="ew", padx=3, pady=3
        )
        ttk.Button(control_frame, text="Xóa kết quả", command=self.clear_results).grid(
            row=0, column=2, sticky="ew", padx=3, pady=3
        )
        for col in range(3):
            control_frame.columnconfigure(col, weight=1)

        algo_frame = ttk.LabelFrame(parent, text="Thuật toán", padding=(6, 6))
        algo_frame.pack(fill=tk.X, pady=(0, 8))
        self.selected_algorithm = tk.StringVar(value=next(iter(self.algorithms)))
        self.cbo_algorithm = ttk.Combobox(
            algo_frame,
            textvariable=self.selected_algorithm,
            values=list(self.algorithms.keys()),
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.cbo_algorithm.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=2)
        self.btn_run = ttk.Button(
            algo_frame,
            text="Chạy",
            command=self.solve_selected_algorithm,
            style="Accent.TButton",
        )
        self.btn_run.grid(row=0, column=1, sticky="ew", pady=2)
        algo_frame.columnconfigure(0, weight=1)

        step_frame = ttk.Frame(parent, style="Panel.TFrame")
        step_frame.pack(fill=tk.X)
        self.btn_prev = ttk.Button(step_frame, text="< Trước", command=self.prev_step, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
        self.lbl_step = ttk.Label(step_frame, text="Bước: 0/0", style="Info.TLabel")
        self.lbl_step.pack(side=tk.LEFT, padx=6)
        self.btn_next = ttk.Button(step_frame, text="Tiếp >", command=self.next_step, state=tk.DISABLED)
        self.btn_next.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(6, 0))

        playback_frame = ttk.Frame(parent, style="Panel.TFrame")
        playback_frame.pack(fill=tk.X, pady=(6, 0))
        self.btn_play = ttk.Button(
            playback_frame,
            text="Tự chạy",
            command=self.toggle_playback,
            state=tk.DISABLED,
            style="Accent.TButton",
        )
        self.btn_play.pack(fill=tk.X)

    def create_right_panel(self, parent):
        tables = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        tables.pack(fill=tk.BOTH, expand=True)

        trace_panel = ttk.LabelFrame(tables, text="Trace chi tiết", padding=8)
        result_panel = ttk.LabelFrame(tables, text="Bảng kết quả", padding=8)
        tables.add(trace_panel, weight=4)
        tables.add(result_panel, weight=1)

        self.create_trace_table(trace_panel)
        self.create_result_table(result_panel)

    def create_trace_table(self, parent):
        columns = ("step", "node", "frontier", "explored")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings")
        self.tree.heading("step", text="Bước")
        self.tree.heading("node", text="Node đang xét")
        self.tree.heading("frontier", text="Frontier")
        self.tree.heading("explored", text="Explored")

        self.tree.column("step", width=70, anchor=tk.CENTER, stretch=False)
        self.tree.column("node", width=180, anchor=tk.W)
        self.tree.column("frontier", width=420, anchor=tk.W)
        self.tree.column("explored", width=420, anchor=tk.W)

        xscrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        yscrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_result_table(self, parent):
        columns = ("algo", "status", "steps", "expanded", "frontier", "explored", "time")
        self.result_tree = ttk.Treeview(parent, columns=columns, show="headings", height=4)
        headings = {
            "algo": "Thuật toán",
            "status": "Kết quả",
            "steps": "Số bước",
            "expanded": "Node trace",
            "frontier": "Frontier max",
            "explored": "Explored max",
            "time": "Thời gian",
        }
        widths = {
            "algo": 130,
            "status": 120,
            "steps": 80,
            "expanded": 100,
            "frontier": 110,
            "explored": 110,
            "time": 110,
        }
        for col in columns:
            self.result_tree.heading(col, text=headings[col])
            self.result_tree.column(col, width=widths[col], anchor=tk.CENTER)

        yscrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=yscrollbar.set)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def update_grid(self, state, sync_start=True):
        self.state = list(state)
        for i, val in enumerate(self.state):
            if val == 0:
                self.buttons[i].config(text="", bg="#cbd5e1", activebackground="#cbd5e1")
            else:
                self.buttons[i].config(text=str(val), bg="#ffffff", fg="#172033", activebackground="#dbeafe")
        self.lbl_current.config(text=f"Hiện tại: {state_to_text(self.state)}")

        if sync_start and hasattr(self, "entry_start"):
            self.entry_start.delete(0, tk.END)
            self.entry_start.insert(0, state_to_text(self.state))

    def move_tile(self, idx):
        if self.path:
            return

        empty_idx = self.state.index(0)
        r1, c1 = divmod(idx, 3)
        r2, c2 = divmod(empty_idx, 3)
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            self.state[empty_idx], self.state[idx] = self.state[idx], self.state[empty_idx]
            self.update_grid(self.state)

    def get_start(self):
        try:
            return parse_puzzle_state(self.entry_start.get())
        except Exception:
            messagebox.showerror("Loi", "Trang thai bat dau khong hop le. Nhap du 9 so tu 0-8.")
            return None

    def apply_start_state(self):
        start = self.get_start()
        if not start:
            return

        self.clear_solution()
        self.update_grid(start)
        self.lbl_status.config(text="Da ap dung trang thai bat dau.")

    def get_goal(self):
        try:
            return parse_puzzle_state(self.entry_goal.get())
        except Exception:
            pass
        messagebox.showerror("Lỗi", "Trạng thái đích không hợp lệ. Nhập đủ 9 số từ 0-8.")
        return None

    def shuffle(self):
        goal = self.get_goal()
        if not goal:
            return

        st = list(goal)
        for _ in range(30):
            empty_idx = st.index(0)
            r, c = divmod(empty_idx, 3)
            moves = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    moves.append(nr * 3 + nc)
            mv = random.choice(moves)
            st[empty_idx], st[mv] = st[mv], st[empty_idx]

        self.update_grid(st)
        self.clear_solution()
        self.lbl_status.config(text="Đã xáo trộn. Chọn một thuật toán để giải.")

    def clear_solution(self):
        self.stop_playback()
        self.path = []
        self.current_step = 0
        self.lbl_step.config(text="Bước: 0/0")
        self.update_step_controls()
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_results(self):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

    def reconstruct_path(self, parent_map, end_state):
        path = []
        curr = end_state
        while curr is not None:
            path.append(curr)
            curr = parent_map[curr]
        path.reverse()
        return path

    def render_trace(self, trace, algo_name):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cập nhật tiêu đề các cột tương ứng với từng thuật toán
        if "CSP" in algo_name:
            if "Min-Conflicts" in algo_name:
                self.tree.heading("step", text="Vòng lặp")
                self.tree.heading("node", text="Trạng thái đại diện")
                self.tree.heading("frontier", text="Chuỗi trạng thái hiện tại")
                self.tree.heading("explored", text="(Không dùng)")
            else:
                self.tree.heading("step", text="Bước")
                self.tree.heading("node", text="Biến gán Si")
                self.tree.heading("frontier", text="Miền giá trị (Domain)")
                self.tree.heading("explored", text="Đường đi tạm thời (Path)")
        elif algo_name in ["Local Search", "Local Beam", "Stochastic HC", "Simulated Annealing"]:
            self.tree.heading("step", text="Bước")
            self.tree.heading("node", text="Trạng thái hiện tại")
            self.tree.heading("frontier", text="Trạng thái kề (Neighbors)")
            self.tree.heading("explored", text="Đường đi đã qua (Path)")
        elif algo_name == "AND-OR Search":
            self.tree.heading("step", text="Bước")
            self.tree.heading("node", text="Trạng thái đang xét")
            self.tree.heading("frontier", text="Các hành động kề (Actions)")
            self.tree.heading("explored", text="Đường đi đệ quy (Path)")
        else:
            self.tree.heading("step", text="Bước")
            self.tree.heading("node", text="Node đang xét")
            self.tree.heading("frontier", text="Frontier")
            self.tree.heading("explored", text="Explored")

        max_display_rows = 1000
        display_trace = trace[:max_display_rows]

        for i, step in enumerate(display_trace):
            node = step["node"]
            n_r0, n_r1, n_r2 = format_state_list([node])
            f_r0, f_r1, f_r2 = format_state_list(step["frontier"])
            e_r0, e_r1, e_r2 = format_state_list(step["explored"])

            val_str = ""
            if "f" in step:
                val_str = f" (f={step['f'].get(node, '?')})"
            elif "h" in step:
                val_str = f" (h={step['h'].get(node, '?')})"
                if "T" in step:
                    val_str += f" [T={step['T']:.3f}]"
            elif "g" in step:
                val_str = f" (g={step['g'].get(node, '?')})"
            elif "limit" in step:
                val_str = f" (d={step.get('depth', '?')}/{step['limit']})"
            elif "csp" in step:
                val_str = f" ({step['csp']})"
            n_r0 += val_str

            self.tree.insert("", tk.END, values=(f"{i + 1}", n_r0, f_r0, e_r0))
            self.tree.insert("", tk.END, values=("", n_r1, f_r1, e_r1))
            self.tree.insert("", tk.END, values=("", n_r2, f_r2, e_r2))
            self.tree.insert("", tk.END, values=("-" * 5, "-" * 24, "-" * 60, "-" * 60))

        if len(trace) > max_display_rows:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    "...",
                    f"Đã ẩn {len(trace) - max_display_rows} bước trace để giao diện ổn định",
                    "",
                    "",
                ),
            )

    def solve_selected_algorithm(self):
        self.solve(self.selected_algorithm.get())

    def solve(self, algo_name):
        if self.is_solving:
            return

        start = self.get_start()
        if not start:
            return

        goal = self.get_goal()
        if not goal:
            return

        if not co_the_giai(start, goal):
            self.clear_solution()
            self.update_grid(start)
            self.lbl_status.config(text="Trạng thái bắt đầu không thể giải tới trạng thái đích.")
            messagebox.showinfo("Kết quả", "Bài toán này không có lời giải với trạng thái đích hiện tại.")
            return

        self.clear_solution()
        self.lbl_status.config(text=f"Đang giải bằng {algo_name}...")
        self.root.update()

        self.update_grid(start)
        self.is_solving = True
        self.btn_run.config(state=tk.DISABLED)
        self.cbo_algorithm.config(state=tk.DISABLED)
        started_at = time.perf_counter()

        worker = threading.Thread(
            target=self.run_algorithm_worker,
            args=(algo_name, start, goal, started_at),
            daemon=True,
        )
        worker.start()

    def run_algorithm_worker(self, algo_name, start, goal, started_at):
        try:
            status, parent_map, trace = self.algorithms[algo_name](start, goal)
            error = None
        except Exception as exc:
            status, parent_map, trace = FAILURE, None, []
            error = exc

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        self.root.after(
            0,
            lambda: self.finish_algorithm(
                status, parent_map, trace, algo_name, goal, elapsed_ms, error
            ),
        )

    def finish_algorithm(self, status, parent_map, trace, algo_name, goal, elapsed_ms, error):
        self.is_solving = False
        self.btn_run.config(state=tk.NORMAL)
        self.cbo_algorithm.config(state="readonly")

        if error is not None:
            self.lbl_status.config(text=f"{algo_name}: lỗi khi chạy thuật toán.")
            messagebox.showerror("Lỗi thuật toán", str(error))
            return

        self.handle_solution(status, parent_map, trace, algo_name, goal, elapsed_ms)

    def handle_solution(self, status, parent_map, trace, algo_name, goal, elapsed_ms):
        self.render_trace(trace, algo_name)

        success = parent_map is not None and goal in parent_map
        path = self.reconstruct_path(parent_map, goal) if success else []
        steps_count = len(path) - 1 if success else "-"
        frontier_max = max((len(step["frontier"]) for step in trace), default=0)
        explored_max = max((len(step["explored"]) for step in trace), default=0)

        self.result_tree.insert(
            "",
            tk.END,
            values=(
                algo_name,
                "Thành công" if success else "Thất bại",
                steps_count,
                len(trace),
                frontier_max,
                explored_max,
                f"{elapsed_ms:.2f} ms",
            ),
        )

        if success:
            self.path = path
            self.current_step = 0
            self.update_step_label()
            self.lbl_status.config(text=f"{algo_name}: tìm thấy đường đi {steps_count} bước.")
            if len(self.path) > 1:
                self.start_playback()
            else:
                self.update_step_controls()
        else:
            self.lbl_status.config(text=f"{algo_name}: không tìm thấy đường đi.")
            messagebox.showinfo("Kết quả", "Không tìm thấy đường đi.")

    def update_step_label(self):
        if self.path:
            self.lbl_step.config(text=f"Bước: {self.current_step}/{len(self.path) - 1}")
            self.update_grid(self.path[self.current_step], sync_start=False)
            self.update_step_controls()

    def update_step_controls(self):
        has_path = bool(self.path)
        can_go_prev = has_path and self.current_step > 0 and not self.is_playing
        can_go_next = has_path and self.current_step < len(self.path) - 1 and not self.is_playing
        can_play = has_path and len(self.path) > 1

        self.btn_prev.config(state=tk.NORMAL if can_go_prev else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if can_go_next else tk.DISABLED)

        if hasattr(self, "btn_play"):
            self.btn_play.config(
                text="Dừng" if self.is_playing else "Tự chạy",
                state=tk.NORMAL if can_play else tk.DISABLED,
            )

    def toggle_playback(self):
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        if not self.path or len(self.path) <= 1:
            return

        self.stop_playback()
        if self.current_step >= len(self.path) - 1:
            self.current_step = 0
            self.update_step_label()

        self.is_playing = True
        self.update_step_controls()
        self.playback_job = self.root.after(self.playback_delay_ms, self.play_next_step)

    def stop_playback(self):
        if self.playback_job is not None:
            try:
                self.root.after_cancel(self.playback_job)
            except tk.TclError:
                pass
            self.playback_job = None
        self.is_playing = False
        if hasattr(self, "btn_play"):
            self.update_step_controls()

    def play_next_step(self):
        self.playback_job = None
        if not self.is_playing or not self.path:
            return

        if self.current_step < len(self.path) - 1:
            self.current_step += 1
            self.update_step_label()
            if self.current_step < len(self.path) - 1:
                self.playback_job = self.root.after(self.playback_delay_ms, self.play_next_step)
            else:
                self.stop_playback()
        else:
            self.stop_playback()

    def prev_step(self):
        self.stop_playback()
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_label()

    def next_step(self):
        self.stop_playback()
        if self.current_step < len(self.path) - 1:
            self.current_step += 1
            self.update_step_label()


if __name__ == "__main__":
    root = tk.Tk()
    app = EightPuzzleGUI(root)
    root.mainloop()
