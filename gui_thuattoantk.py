import random
import time
import tkinter as tk
from tkinter import messagebox, ttk

from thuattoantk import (
    A_Star,
    BFS,
    DFS,
    GOAL,
    Greedy_Search,
    IDS,
    Local_Beam_Search,
    Local_Search,
    Stochastic_Hill_Climbing,
    UCS,
)


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
            "BFS": BFS,
            "DFS": DFS,
            "IDS": IDS,
            "UCS": UCS,
        }

        self.state = list(GOAL)
        self.buttons = []
        self.path = []
        self.current_step = 0

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

        left_frame = ttk.Frame(main, style="Panel.TFrame", padding=16)
        right_frame = ttk.Frame(main, style="Panel.TFrame", padding=12)
        main.add(left_frame, weight=1)
        main.add(right_frame, weight=3)

        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent):
        ttk.Label(parent, text="Bàn cờ", style="SubHeader.TLabel").pack(anchor=tk.W)

        grid_frame = tk.Frame(parent, bg="#334155", bd=0, padx=6, pady=6)
        grid_frame.pack(pady=(10, 14))

        for i in range(9):
            btn = tk.Button(
                grid_frame,
                text="",
                font=("Segoe UI", 28, "bold"),
                width=3,
                height=1,
                relief=tk.FLAT,
                command=lambda idx=i: self.move_tile(idx),
            )
            btn.grid(row=i // 3, column=i % 3, padx=4, pady=4, sticky="nsew")
            self.buttons.append(btn)

        info_frame = ttk.Frame(parent, style="Panel.TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 12))
        self.lbl_current = ttk.Label(info_frame, text="", style="Info.TLabel")
        self.lbl_current.pack(anchor=tk.W)
        self.lbl_status = ttk.Label(
            info_frame,
            text="Sẵn sàng. Chọn thuật toán để giải hoặc tự di chuyển ô.",
            style="Status.TLabel",
            wraplength=330,
        )
        self.lbl_status.pack(anchor=tk.W, pady=(6, 0))

        goal_frame = ttk.LabelFrame(parent, text="Trạng thái đích", padding=10)
        goal_frame.pack(fill=tk.X, pady=(0, 12))
        self.entry_goal = ttk.Entry(goal_frame, font=("Consolas", 11))
        self.entry_goal.insert(0, "1 2 3 4 5 6 7 8 0")
        self.entry_goal.pack(fill=tk.X)

        control_frame = ttk.LabelFrame(parent, text="Điều khiển", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 12))
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

        algo_frame = ttk.LabelFrame(parent, text="Thuật toán", padding=(10, 8))
        algo_frame.pack(fill=tk.X, pady=(0, 12))
        self.selected_algorithm = tk.StringVar(value=next(iter(self.algorithms)))
        self.cbo_algorithm = ttk.Combobox(
            algo_frame,
            textvariable=self.selected_algorithm,
            values=list(self.algorithms.keys()),
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.cbo_algorithm.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=2)
        ttk.Button(
            algo_frame,
            text="Chạy",
            command=self.solve_selected_algorithm,
            style="Accent.TButton",
        ).grid(row=0, column=1, sticky="ew", pady=2)
        algo_frame.columnconfigure(0, weight=1)

        step_frame = ttk.Frame(parent, style="Panel.TFrame")
        step_frame.pack(fill=tk.X)
        self.btn_prev = ttk.Button(step_frame, text="< Trước", command=self.prev_step, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
        self.lbl_step = ttk.Label(step_frame, text="Bước: 0/0", style="Info.TLabel")
        self.lbl_step.pack(side=tk.LEFT, padx=6)
        self.btn_next = ttk.Button(step_frame, text="Tiếp >", command=self.next_step, state=tk.DISABLED)
        self.btn_next.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(6, 0))

    def create_right_panel(self, parent):
        tables = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        tables.pack(fill=tk.BOTH, expand=True)

        trace_panel = ttk.LabelFrame(tables, text="Trace chi tiết", padding=8)
        result_panel = ttk.LabelFrame(tables, text="Bảng kết quả", padding=8)
        tables.add(trace_panel, weight=3)
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
        self.result_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
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

    def update_grid(self, state):
        self.state = list(state)
        for i, val in enumerate(self.state):
            if val == 0:
                self.buttons[i].config(text="", bg="#cbd5e1", activebackground="#cbd5e1")
            else:
                self.buttons[i].config(text=str(val), bg="#ffffff", fg="#172033", activebackground="#dbeafe")
        self.lbl_current.config(text=f"Hiện tại: {state_to_text(self.state)}")

    def move_tile(self, idx):
        if self.path:
            return

        empty_idx = self.state.index(0)
        r1, c1 = divmod(idx, 3)
        r2, c2 = divmod(empty_idx, 3)
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            self.state[empty_idx], self.state[idx] = self.state[idx], self.state[empty_idx]
            self.update_grid(self.state)

    def get_goal(self):
        try:
            s = self.entry_goal.get().replace(",", " ").split()
            goal = tuple(int(x) for x in s)
            if len(goal) == 9 and set(goal) == set(range(9)):
                return goal
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
        self.path = []
        self.current_step = 0
        self.lbl_step.config(text="Bước: 0/0")
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
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

    def render_trace(self, trace):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, step in enumerate(trace):
            node = step["node"]
            n_r0, n_r1, n_r2 = format_state_list([node])
            f_r0, f_r1, f_r2 = format_state_list(step["frontier"])
            e_r0, e_r1, e_r2 = format_state_list(step["explored"])

            val_str = ""
            if "f" in step:
                val_str = f" (f={step['f'].get(node, '?')})"
            elif "h" in step:
                val_str = f" (h={step['h'].get(node, '?')})"
            elif "g" in step:
                val_str = f" (g={step['g'].get(node, '?')})"
            elif "limit" in step:
                val_str = f" (d={step.get('depth', '?')}/{step['limit']})"
            n_r0 += val_str

            self.tree.insert("", tk.END, values=(f"{i + 1}", n_r0, f_r0, e_r0))
            self.tree.insert("", tk.END, values=("", n_r1, f_r1, e_r1))
            self.tree.insert("", tk.END, values=("", n_r2, f_r2, e_r2))
            self.tree.insert("", tk.END, values=("-" * 5, "-" * 24, "-" * 60, "-" * 60))

    def solve_selected_algorithm(self):
        self.solve(self.selected_algorithm.get())

    def solve(self, algo_name):
        goal = self.get_goal()
        if not goal:
            return

        self.clear_solution()
        self.lbl_status.config(text=f"Đang giải bằng {algo_name}...")
        self.root.update()

        start = tuple(self.state)
        started_at = time.perf_counter()
        status, parent_map, trace = self.algorithms[algo_name](start, goal)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        self.handle_solution(status, parent_map, trace, algo_name, goal, elapsed_ms)

    def handle_solution(self, status, parent_map, trace, algo_name, goal, elapsed_ms):
        self.render_trace(trace)

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
            self.btn_next.config(state=tk.NORMAL if len(self.path) > 1 else tk.DISABLED)
            self.btn_prev.config(state=tk.DISABLED)
            self.lbl_status.config(text=f"{algo_name}: tìm thấy đường đi {steps_count} bước.")
        else:
            self.lbl_status.config(text=f"{algo_name}: không tìm thấy đường đi.")
            messagebox.showinfo("Kết quả", "Không tìm thấy đường đi.")

    def update_step_label(self):
        if self.path:
            self.lbl_step.config(text=f"Bước: {self.current_step}/{len(self.path) - 1}")
            self.update_grid(self.path[self.current_step])

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_label()
            self.btn_next.config(state=tk.NORMAL)
            if self.current_step == 0:
                self.btn_prev.config(state=tk.DISABLED)

    def next_step(self):
        if self.current_step < len(self.path) - 1:
            self.current_step += 1
            self.update_step_label()
            self.btn_prev.config(state=tk.NORMAL)
            if self.current_step == len(self.path) - 1:
                self.btn_next.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = EightPuzzleGUI(root)
    root.mainloop()
