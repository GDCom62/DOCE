import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import random
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk

def inicializar_banco():
    conn = sqlite3.connect("loja_doces.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            codigo TEXT PRIMARY KEY, nome TEXT, preco REAL, estoque INTEGER,
            fabricacao TEXT, recebimento TEXT, vencimento TEXT, imagem TEXT, ativo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            usuario TEXT PRIMARY KEY, senha TEXT, nome TEXT, cargo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL
        )
    """)
    for col in ["fabricacao", "recebimento", "vencimento", "imagem", "ativo"]:
        try: cursor.execute(f"ALTER TABLE produtos ADD COLUMN {col} TEXT")
        except: pass
    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    if cursor.fetchone() == 0:
        cursor.execute("INSERT INTO funcionarios VALUES ('admin', '1234', 'Gerente', 'Administrador')")
        cursor.execute("INSERT INTO funcionarios VALUES ('caixa', '4321', 'Operador', 'Caixa')")
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone() == 0:
        cursor.execute("INSERT INTO produtos VALUES ('1001', 'Brigadeiro Gourmet Gp', 4.50, 99, '19/10/2026', '19/10/2026', '26/10/2026', '', 'Sim')")
    conn.commit()
    conn.close()

class TelaLogin:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.root.title("Candy Shop - Login")
        self.root.geometry("400x300")
        self.root.configure(bg="#F8F9FA")
        
        frame = tk.Frame(self.root, bg="white", bd=0, relief="flat")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=320, height=250)
        
        tk.Label(frame, text="Candy Shop", font=("Segoe UI", 16, "bold"), bg="white", fg="#FF6B8B").pack(pady=15)
        tk.Label(frame, text="USUÁRIO", font=("Segoe UI", 9, "bold"), bg="white", fg="#6C757D").pack(anchor="w", padx=30)
        self.txt_u = tk.Entry(frame, width=24, font=("Segoe UI", 11), bg="#F1F3F5", relief="flat")
        self.txt_u.pack(pady=5)
        self.txt_u.focus_set()
        
        tk.Label(frame, text="SENHA", font=("Segoe UI", 9, "bold"), bg="white", fg="#6C757D").pack(anchor="w", padx=30)
        self.txt_s = tk.Entry(frame, width=24, font=("Segoe UI", 11), bg="#F1F3F5", relief="flat", show="*")
        self.txt_s.pack(pady=5)
        self.txt_s.bind("<Return>", lambda e: self.logar())
        
        tk.Button(frame, text="Entrar", bg="#FF6B8B", fg="white", font=("Segoe UI", 11, "bold"), command=self.logar, relief="flat", cursor="hand2", width=18).pack(pady=15)

    def logar(self):
        u = self.txt_u.get().strip()
        s = self.txt_s.get().strip()
        if u == "admin" and s == "1234":
            self.callback("Gerente", "Administrador")
            return
        if u == "caixa" and s == "4321":
            self.callback("Operador", "Caixa")
            return
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome, cargo FROM funcionarios WHERE usuario=? AND senha=?", (u, s))
        res = cursor.fetchone()
        conn.close()
        if res: self.callback(str(res), str(res))
        else: messagebox.showerror("Erro", "Usuário ou Senha incorretos!")

class LojaDocesApp:
    def __init__(self, root, nome, cargo):
        self.root = root
        self.nome = str(nome)
        self.cargo = str(cargo)
        self.root.title("Candy Shop - Gestão Comercial")
        self.root.geometry("1200x700")
        self.root.configure(bg="#F8F9FA")
        self.carrinho = []
        self.cache_imagens = {}
        
        self.f_menu = tk.Frame(self.root, bg="white", bd=0, width=200)
        self.f_menu.pack(side="left", fill="y")
        self.f_menu.pack_propagate(False)
        
        if os.path.exists("logo_empresa.png"):
            try:
                img_emp = Image.open("logo_empresa.png")
                w_percent = (160 / float(img_emp.size[0]))
                h_size = int((float(img_emp.size[1]) * float(w_percent)))
                img_emp = img_emp.resize((160, h_size), Image.Resampling.LANCZOS)
                self.img_logo_emp = ImageTk.PhotoImage(img_emp)
                tk.Label(self.f_menu, image=self.img_logo_emp, bg="white").pack(pady=15)
            except: tk.Label(self.f_menu, text="Candy Shop", font=("Segoe UI", 16, "bold"), bg="white", fg="#FF6B8B").pack(pady=25)
        else: tk.Label(self.f_menu, text="Candy Shop", font=("Segoe UI", 16, "bold"), bg="white", fg="#FF6B8B").pack(pady=25)
        
        self.btn_pdv = tk.Button(self.f_menu, text="🧁 Balcão de Vendas", font=("Segoe UI", 10, "bold"), bg="#FFF0F2", fg="#FF6B8B", relief="flat", anchor="w", padx=20, pady=12, command=lambda: self.mudar_aba(0))
        self.btn_pdv.pack(fill="x", padx=10, pady=2)
        
        self.btn_est = tk.Button(self.f_menu, text="📦 Almoxarifado", font=("Segoe UI", 10), bg="white", fg="#495057", relief="flat", anchor="w", padx=20, pady=12, command=lambda: self.mudar_aba(1))
        self.btn_est.pack(fill="x", padx=10, pady=2)
        
        self.btn_rel = tk.Button(self.f_menu, text="📊 Relatórios", font=("Segoe UI", 10), bg="white", fg="#495057", relief="flat", anchor="w", padx=20, pady=12, command=lambda: self.mudar_aba(2))
        self.btn_rel.pack(fill="x", padx=10, pady=2)
            
        f_rodape_dev = tk.Frame(self.f_menu, bg="white")
        f_rodape_dev.pack(side="bottom", fill="x", pady=15)
        if os.path.exists("logo_desenvolvedor.png"):
            try:
                img_dev = Image.open("logo_desenvolvedor.png")
                w_percent = (140 / float(img_dev.size[0]))
                h_size = int((float(img_dev.size[1]) * float(w_percent)))
                img_dev = img_dev.resize((140, h_size), Image.Resampling.LANCZOS)
                self.img_logo_dev = ImageTk.PhotoImage(img_dev)
                tk.Label(f_rodape_dev, image=self.img_logo_dev, bg="white").pack()
            except: tk.Label(f_rodape_dev, text="Dev: @SweetManager", font=("Segoe UI", 8, "bold"), bg="white", fg="#ADB5BD").pack()
        else: tk.Label(f_rodape_dev, text="Dev: @SweetManager", font=("Segoe UI", 8, "bold"), bg="white", fg="#ADB5BD").pack()
        
        self.f_conteudo = tk.Frame(self.root, bg="#F8F9FA")
        self.f_conteudo.pack(side="right", fill="both", expand=True)
        self.f_topo = tk.Frame(self.f_conteudo, bg="#F8F9FA")
        self.f_topo.pack(fill="x", padx=20, pady=15)
        
        self.txt_pesquisa_nome = tk.Entry(self.f_topo, font=("Segoe UI", 11), bg="white", relief="flat", fg="#495057")
        self.txt_pesquisa_nome.insert(0, "Procurar doce...")
        self.txt_pesquisa_nome.pack(fill="x", expand=True, ipady=8)
        self.txt_pesquisa_nome.bind("<FocusIn>", lambda e: self.txt_pesquisa_nome.delete(0, tk.END) if "Procurar" in self.txt_pesquisa_nome.get() else None)
        self.txt_pesquisa_nome.bind("<KeyRelease>", lambda e: self.atualizar_vitrine_doces())
        
        self.txt_bipe_caixa = tk.Entry(self.f_topo, width=1, bg="#F8F9FA", relief="flat", bd=0, fg="#F8F9FA")
        self.txt_bipe_caixa.pack(side="right")
        self.txt_bipe_caixa.bind("<Return>", lambda e: self.processar_bipe_scanner())
        
        self.frames_abas = []
        for _ in range(3):
            f = tk.Frame(self.f_conteudo, bg="#F8F9FA")
            self.frames_abas.append(f)
            
        self.montar_pdv()
        self.montar_estoque()
        self.montar_relatorios()
        
        self.mudar_aba(0)
        self.verificar_vencimentos()

    def mudar_aba(self, idx):
        for f in self.frames_abas: f.pack_forget()
        self.frames_abas[idx].pack(fill="both", expand=True, padx=20, pady=5)
        botoes = [self.btn_pdv, self.btn_est, self.btn_rel]
        for i, btn in enumerate(botoes):
            if i == idx: btn.config(bg="#FFF0F2", fg="#FF6B8B", font=("Segoe UI", 10, "bold"))
            else: btn.config(bg="white", fg="#495057", font=("Segoe UI", 10))
        if idx == 0: self.root.after(100, lambda: self.txt_bipe_caixa.focus_set())

    def verificar_vencimentos(self):
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome, vencimento FROM produtos")
        linhas = cursor.fetchall()
        conn.close()
        hoje = datetime.now().date()
        alertas = []
        for nome, venc_str in linhas:
            if not venc_str: continue
            venc_limpo = venc_str.strip()
            for fmt in ["%d/%m/%y", "%d/%m/%Y"]:
                try:
                    d_venc = datetime.strptime(venc_limpo, fmt).date()
                    diferenca = (d_venc - hoje).days
                    if diferenca < 0: alertas.append(f"❌ {nome} - JÁ VENCEU EM {venc_limpo}!")
                    elif diferenca <= 7: alertas.append(f"⚠️ {nome} - Vence em {diferenca} dias ({venc_limpo})")
                    break
                except: continue
        if alertas: messagebox.showwarning("⚠️ CONTROLE DE VALIDADE", "\n".join(alertas))

    def montar_pdv(self):
        f_pdv = self.frames_abas[0]
        self.f_vitrine_container = tk.Frame(f_pdv, bg="#F8F9FA")
        self.f_vitrine_container.place(relx=0.0, rely=0.0, relwidth=0.72, relheight=1.0)
        
        self.canvas_vitrine = tk.Canvas(self.f_vitrine_container, bg="#F8F9FA", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.f_vitrine_container, orient="vertical", command=self.canvas_vitrine.yview)
        self.f_cards_grid = tk.Frame(self.canvas_vitrine, bg="#F8F9FA")
        self.f_cards_grid.bind("<Configure>", lambda e: self.canvas_vitrine.configure(scrollregion=self.canvas_vitrine.bbox("all")))
        self.canvas_vitrine.create_window((0, 0), window=self.f_cards_grid, anchor="nw")
        self.canvas_vitrine.configure(yscrollcommand=scrollbar.set)
        self.canvas_vitrine.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        f_caixa_dir = tk.Frame(f_pdv, bg="white", bd=0)
        f_caixa_dir.place(relx=0.74, rely=0.0, relwidth=0.26, relheight=0.95)
        tk.Label(f_caixa_dir, text="Sacola de Compras", font=("Segoe UI", 12, "bold"), bg="white", fg="#343A40").pack(pady=15, anchor="w", padx=15)
        
        self.tree_sacola = ttk.Treeview(f_caixa_dir, columns=("N", "Q", "T"), show="headings", height=12)
        self.tree_sacola.heading("N", text="Doce")
        self.tree_sacola.heading("Q", text="Qtd")
        self.tree_sacola.heading("T", text="Total")
        self.tree_sacola.column("N", width=100)
        self.tree_sacola.column("Q", width=35, anchor="center")
        self.tree_sacola.column("T", width=65, anchor="e")
        self.tree_sacola.pack(fill="x", padx=15)
        
        f_comercial = tk.Frame(f_caixa_dir, bg="#343A40", bd=0)
        f_comercial.pack(fill="x", padx=15, pady=15)
        self.lbl_tot = tk.Label(f_comercial, text="R$ 0,00", font=("Segoe UI", 20, "bold"), fg="#28A745", bg="#343A40")
        self.lbl_tot.pack(pady=12)
        
        tk.Label(f_caixa_dir, text="Forma de Pagamento:", bg="white", font=("Segoe UI", 9, "bold"), fg="#6C757D").pack(anchor="w", padx=15)
        self.cb_pag = ttk.Combobox(f_caixa_dir, values=["Dinheiro", "Pix", "Cartão de Débito", "Cartão de Crédito"], state="readonly", font=("Segoe UI", 10))
        self.cb_pag.set("Pix")
        self.cb_pag.pack(fill="x", padx=15, pady=5)
        
        tk.Button(f_caixa_dir, text="Limpar Venda", bg="#6C757D", fg="white", font=("Segoe UI", 10, "bold"), command=self.limpar_caixa, relief="flat").pack(fill="x", padx=15, pady=5)
        tk.Button(f_caixa_dir, text="Emitir Cupom (SAT)", bg="#FF6B8B", fg="white", font=("Segoe UI", 11, "bold"), command=self.emitir_cupom, relief="flat").pack(fill="x", padx=15, pady=5)
        
        f_barra_hw = tk.Frame(f_caixa_dir, bg="white")
        f_barra_hw.pack(fill="x", padx=15, pady=5)
        tk.Button(f_barra_hw, text="Bipar Código (Sorteio)", bg="#6C757D", fg="white", command=self.simular_bipe_real).pack(fill="x", pady=2)
        self.atualizar_vitrine_doces()

    def processar_bipe_scanner(self):
        codigo_bipado = self.txt_bipe_caixa.get().strip()
        self.txt_bipe_caixa.delete(0, tk.END)
        if codigo_bipado:
            conn = sqlite3.connect("loja_doces.db")
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, ativo FROM produtos WHERE codigo=?", (codigo_bipado,))
            res = cursor.fetchone()
            conn.close()
            if res:
                if str(res[1]) == "Não": messagebox.showwarning("Aviso", "Esta mercadoria está inativa no mural!")
                else: self.adicionar_por_card(codigo_bipado)
            else: messagebox.showerror("Leitor", f"Código [{codigo_bipado}] não cadastrado!")
        self.txt_bipe_caixa.focus_set()

    def atualizar_vitrine_doces(self):
        for widget in self.f_cards_grid.winfo_children(): widget.destroy()
        termo = self.txt_pesquisa_nome.get().strip().lower()
        if "procurar" in termo: termo = ""
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        try: cursor.execute("SELECT codigo, nome, preco, estoque, imagem FROM produtos WHERE lower(nome) LIKE ? AND (ativo = 'Sim' OR ativo IS NULL)", (f"%{termo}%",))
        except: cursor.execute("SELECT codigo, nome, preco, estoque, imagem FROM produtos WHERE lower(nome) LIKE ?", (f"%{termo}%",))
        doces = cursor.fetchall()
        conn.close()
        colunas_maximas, linha, coluna = 4, 0, 0
        for cod, nome, preco, estoque, img_path in doces:
            f_card = tk.Frame(self.f_cards_grid, bg="white", bd=0, padx=12, pady=12)
            f_card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nsew")
            foto_carregada = False
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path).resize((130, 110), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    self.cache_imagens[cod] = img_tk
                    tk.Label(f_card, image=img_tk, bg="white").pack(pady=5)
                    foto_carregada = True
                except: pass
            if not foto_carregada: tk.Label(f_card, text="🍬", font=("Segoe UI", 38), bg="white", fg="#FF6B8B").pack(pady=15)
            tk.Label(f_card, text=f"R$ {preco:.2f}", font=("Segoe UI", 10, "bold"), bg="#FFF0F2", fg="#FF6B8B", padx=6, pady=2).pack(pady=2)
            nome_resumido = nome[:18] + "..." if len(nome) > 18 else nome
            tk.Label(f_card, text=nome_resumido, font=("Segoe UI", 10, "bold"), bg="white", fg="#343A40", wraplength=130, justify="center").pack(pady=5)
            tk.Button(f_card, text="+ Adicionar", bg="#FF6B8B", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=lambda c=cod: self.adicionar_por_card(c)).pack(fill="x", pady=5)
            coluna += 1
            if coluna >= colunas_maximas: coluna = 0; linha += 1

    def adicionar_por_card(self, codigo_produto):
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome, preco, estoque FROM produtos WHERE codigo=?", (codigo_produto,))
        res = cursor.fetchone()
        conn.close()
        if res:
            nome, preco, estoque = res
            qtd_na_sacola = sum(item["qtd"] for item in self.carrinho if item["codigo"] == codigo_produto)
            if estoque <= qtd_na_sacola:
                messagebox.showwarning("Estoque", "Quantidade máxima atingida!")
                return
            self.carrinho.append({"codigo": codigo_produto, "nome": nome, "qtd": 1, "preco": preco})
            self.atualizar_car()

    def atualizar_car(self):
        for item in self.tree_sacola.get_children(): self.tree_sacola.delete(item)
        tot = 0
        itens_agrupados = {}
        for item in self.carrinho:
            cod = item["codigo"]
            if cod in itens_agrupados:
                itens_agrupados[cod]["qtd"] += 1
                itens_agrupados[cod]["total"] += item["preco"]
            else: itens_agrupados[cod] = {"nome": item["nome"], "qtd": 1, "total": item["preco"]}
            tot += item["preco"]
        for cod, dados in itens_agrupados.items():
            self.tree_sacola.insert("", "end", values=(dados["nome"], dados["qtd"], f"R$ {dados['total']:.2f}"))
        self.lbl_tot.config(text=f"R$ {tot:.2f}")

    def limpar_caixa(self):
        self.carrinho.clear()
        self.atualizar_car()

    def emitir_cupom(self):
        if not self.carrinho: return
        tot = sum(i["preco"] for i in self.carrinho)
        forma_pagto = self.cb_pag.get()
        agora = datetime.now()
        
        if forma_pagto == "Pix":
            pop_pix = tk.Toplevel(self.root)
            pop_pix.title("Pagamento via Pix SAT")
            pop_pix.geometry("340x240")
            pop_pix.grab_set()
            tk.Label(pop_pix, text="💠 INSTANTÂNEO PIX 💠", font=("Segoe UI", 12, "bold"), fg="#17A2B8").pack(pady=10)
            tk.Label(pop_pix, text=f"VALOR: R$ {tot:.2f}", font=("Segoe UI", 14, "bold"), fg="#28A745").pack(pady=5)
            txt_copia = tk.Entry(pop_pix, font=("Segoe UI", 9))
            txt_copia.insert(0, f"00020126360014BR.GOV.BCB.PIX0114candyshop{random.randint(1000,9999)}")
            txt_copia.pack(fill="x", padx=20, pady=2)
            tk.Button(pop_pix, text="✅ Confirmar Recebimento", bg="#28A745", fg="white", command=pop_pix.destroy, relief="flat").pack(pady=10)
            self.root.wait_window(pop_pix)
            
        elif forma_pagto in ["Cartão de Débito", "Cartão de Crédito"]:
            pop_cartao = tk.Toplevel(self.root)
            pop_cartao.title("Conexão Pinpad")
            pop_cartao.geometry("320x180")
            pop_cartao.grab_set()
            tk.Label(pop_cartao, text="💳 TEF / MAQUININHA", font=("Segoe UI", 11, "bold"), fg="#007BFF").pack(pady=10)
            lbl_status = tk.Label(pop_cartao, text="Aguardando senha...", font=("Segoe UI", 10, "bold"), fg="#DC3545")
            lbl_status.pack(pady=5)
            def aprovar():
                lbl_status.config(text="Transação Aprovada! 🟩", fg="#28A745")
                tk.Button(pop_cartao, text="Concluir", bg="#28A745", fg="white", font=("Segoe UI", 9, "bold"), command=pop_cartao.destroy, relief="flat").pack(pady=10)
            pop_cartao.after(1500, aprovar)
            self.root.wait_window(pop_cartao)
            
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        for i in self.carrinho:
            cursor.execute("UPDATE produtos SET estoque = estoque - 1 WHERE codigo=?", (i["codigo"],))
            cursor.execute("INSERT INTO vendas (data, total) VALUES (?, ?)", (agora.strftime("%Y-%m-%d %H:%M:%S"), i["preco"]))
        conn.commit()
        conn.close()
        
        num = random.randint(100000, 999999)
        with open(f"cupom_fiscal_{num}.txt", "w", encoding="utf-8") as f:
            f.write(f"============ CANDY SHOP ============\nCUPOM FISCAL SAT\nDATA: {agora.strftime('%d/%m/%Y %H:%M:%S')}\nFORMA: {forma_pagto.upper()}\nTOTAL: R$ {tot:.2f}\n")
        messagebox.showinfo("Sucesso", f"Venda fechada via [{forma_pagto}]!\nCupom SAT Nº {num} gerado.")
        self.limpar_caixa()
        self.atualizar_vitrine_doces()
        self.atualizar_est()

    def simular_bipe_real(self):
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        cursor.execute("SELECT codigo FROM produtos WHERE (ativo = 'Sim' OR ativo IS NULL) ORDER BY random() LIMIT 1")
        res = cursor.fetchone()
        conn.close()
        if res: self.adicionar_por_card(str(res[0]))
        else: messagebox.showinfo("Simulador", "Cadastre doces ativos no Almoxarifado para testar!")

    def montar_estoque(self):
        f_est = self.frames_abas[1]
        self.caminho_foto_selecionada = ""
        f_top = tk.Frame(f_est, bg="white", bd=0, padx=15, pady=10)
        f_top.pack(fill="x", padx=10, pady=5)
        
        labels = ["Cod:", "Nome:", "Preço:", "Qtd:", "Fab (DD/MM/AA):", "Rec (DD/MM/AA):", "Venc (DD/MM/AA):"]
        self.entradas = []
        for idx, text in enumerate(labels):
            tk.Label(f_top, text=text, bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=idx, padx=4, pady=2, sticky="w")
            e = tk.Entry(f_top, width=11, font=("Segoe UI", 10), bg="#F1F3F5", relief="flat")
            e.grid(row=1, column=idx, padx=4, pady=2)
            self.entradas.append(e)
            
        tk.Label(f_top, text="Disponível Venda:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=7, padx=4, pady=2, sticky="w")
        self.cb_ativo = ttk.Combobox(f_top, values=["Sim", "Não"], state="readonly", width=6, font=("Segoe UI", 10))
        self.cb_ativo.set("Sim")
        self.cb_ativo.grid(row=1, column=7, padx=4, pady=2)
        
        tk.Button(f_top, text="📸 Foto", bg="#17A2B8", fg="white", font=("Segoe UI", 9, "bold"), command=self.selecionar_foto_produto, relief="flat").grid(row=1, column=8, padx=4)
        tk.Button(f_top, text="✏️ Alterar Doce", bg="#28A745", fg="white", font=("Segoe UI", 9, "bold"), command=self.lancar_p, relief="flat").grid(row=1, column=9, padx=4)
        tk.Button(f_top, text="Cadastrar Novo", bg="#FF6B8B", fg="white", font=("Segoe UI", 10, "bold"), command=self.lancar_p, relief="flat").grid(row=1, column=10, padx=4)
        
        self.tree_est = ttk.Treeview(f_est, columns=("C", "N", "P", "E", "F", "R", "V", "A"), show="headings")
        headings = [("C", "Código"), ("N", "Nome"), ("P", "Preço"), ("E", "Estoque"), ("F", "Fabricação"), ("R", "Recebimento"), ("V", "Vencimento"), ("A", "No Mural?")]
        for col, text in headings:
            self.tree_est.heading(col, text=text)
            self.tree_est.column(col, width=95, anchor="center")
        self.tree_est.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_est.bind("<Double-1>", self.carregar_doce_para_edicao)
        self.atualizar_est()

    def selecionar_foto_produto(self):
        caminho = filedialog.askopenfilename(title="Escolha a foto", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if caminho: self.caminho_foto_selecionada = caminho; messagebox.showinfo("Foto", "Carregada!")

    def carregar_doce_para_edicao(self, event):
        item = self.tree_est.selection()
        if item:
            valores = self.tree_est.item(item, "values")
            for i in range(7):
                self.entradas[i].delete(0, tk.END)
                self.entradas[i].insert(0, valores[i])
            self.cb_ativo.set(valores[7])
            conn = sqlite3.connect("loja_doces.db")
            cursor = conn.cursor()
            cursor.execute("SELECT imagem FROM produtos WHERE codigo=?", (valores[0],))
            img_res = cursor.fetchone()
            conn.close()
            if img_res and img_res[0]: 
                self.caminho_foto_selecionada = img_res[0]
            messagebox.showinfo("Edição Ativa", f"Modifique os dados do Doce [{valores[1]}] nas caixas superiores e clique em '✏️ Alterar Doce' para salvar!")

    def lancar_p(self):
        d = [e.get().strip() for e in self.entradas]
        status_mural = self.cb_ativo.get()
        if not d[0] or not d[1] or not d[2] or not d[3]:
            messagebox.showerror("Erro", "Código, Nome, Preço e Qtd são obrigatórios!")
            return
        preco_texto = d[2].replace(",", ".")
        try: 
            preco_float = float(preco_texto)
            qtd_int = int(d[3])
        except: 
            messagebox.showerror("Erro", "Valores numéricos de preço ou quantidade incorretos!")
            return
            
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        try: cursor.execute("ALTER TABLE produtos ADD COLUMN ativo TEXT")
        except: pass
        
        try: 
            cursor.execute("INSERT INTO produtos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (d[0], d[1], preco_float, qtd_int, d[4], d[5], d[6], self.caminho_foto_selecionada, status_mural))
        except: 
            cursor.execute("UPDATE produtos SET nome=?, preco=?, estoque=?, fabricacao=?, recebimento=?, vencimento=?, imagem=?, ativo=? WHERE codigo=?", (d[1], preco_float, qtd_int, d[4], d[5], d[6], self.caminho_foto_selecionada, status_mural, d[0]))
            
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produto gravado e atualizado permanentemente!")
        self.caminho_foto_selecionada = ""
        self.cb_ativo.set("Sim")
        self.atualizar_est()
        self.atualizar_vitrine_doces()
        for e in self.entradas: 
            e.delete(0, tk.END)

    def atualizar_est(self):
        for item in self.tree_est.get_children(): self.tree_est.delete(item)
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nome, preco, estoque, fabricacao, recebimento, vencimento, ativo FROM produtos")
        for r in cursor.fetchall():
            self.tree_est.insert("", "end", values=(r[0], r[1], f"R$ {r[2]:.2f}", f"{r[3]} un", r[4], r[5], r[6], r[7] if r[7] else "Sim"))
        conn.close()

    def montar_relatorios(self):
        f_rel = self.frames_abas[2]
        f_top = tk.Frame(f_rel, bg="white", bd=0, padx=15, pady=15)
        f_top.pack(fill="x", padx=10, pady=10)
        self.v_f = tk.StringVar(value="diario")
        tk.Radiobutton(f_top, text="Diário", variable=self.v_f, value="diario", command=self.atualizar_rel, bg="white").pack(side="left", padx=15)
        tk.Radiobutton(f_top, text="Semanal", variable=self.v_f, value="semanal", command=self.atualizar_rel, bg="white").pack(side="left", padx=15)
        tk.Radiobutton(f_top, text="Mensal", variable=self.v_f, value="mensal", command=self.atualizar_rel, bg="white").pack(side="left", padx=15)
        tk.Radiobutton(f_top, text="Anual", variable=self.v_f, value="anual", command=self.atualizar_rel, bg="white").pack(side="left", padx=15)
        self.lbl_res = tk.Label(f_rel, text="", font=("Segoe UI", 16, "bold"), fg="#28A745")
        self.lbl_res.pack(padx=20, pady=20, anchor="w")
        self.atualizar_rel()

    def atualizar_rel(self):
        p = self.v_f.get()
        hoje = datetime.now().date()
        conn = sqlite3.connect("loja_doces.db")
        cursor = conn.cursor()
        cursor.execute("SELECT data, total FROM vendas")
        rows = cursor.fetchall()
        conn.close()
        tot = 0.0
        for r_data, r_total in rows:
            try: d = datetime.strptime(r_data, "%Y-%m-%d %H:%M:%S").date()
            except: continue
            if p == "diario" and d == hoje: tot += r_total
            elif p == "semanal" and d >= (hoje - timedelta(days=7)): tot += r_total
            elif p == "mensal" and d.month == hoje.month and d.year == hoje.year: tot += r_total
            elif p == "anual" and d.year == hoje.year: tot += r_total
        self.lbl_res.config(text=f"FATURAMENTO REAL REGISTRADO: R$ {tot:.2f}")

def iniciar_sistema(nome, cargo):
    global j_l
    if 'j_l' in globals() and j_l:
        try: j_l.destroy()
        except: pass
    root_principal = tk.Tk()
    LojaDocesApp(root_principal, nome, cargo)
    root_principal.mainloop()

if __name__ == "__main__":
    inicializar_banco()
    j_l = tk.Tk()
    TelaLogin(j_l, iniciar_sistema)
    j_l.mainloop()

