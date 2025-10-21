import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import requests
import threading
import time
from datetime import datetime

class SolanaPaymentSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Paiement USDT via le réseau Solana")
        self.root.geometry("1200x700")
        
        # Adresse du contrat USDT sur Solana
        self.USDT_TOKEN = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
        self.usdt_to_currency = 1.0
        self.selected_currency = "cad"
        self.monitoring = False
        self.transaction_hash = None
        self.initial_balance = None  # Solde USDT initial avant la transaction
        
        # Liste des devises populaires (code: nom)
        self.currencies = {
            "usd": "🇺🇸 USD - Dollar américain",
            "eur": "🇪🇺 EUR - Euro",
            "cad": "🇨🇦 CAD - Dollar canadien",
            "gbp": "🇬🇧 GBP - Livre sterling",
            "jpy": "🇯🇵 JPY - Yen japonais",
            "aud": "🇦🇺 AUD - Dollar australien",
            "chf": "🇨🇭 CHF - Franc suisse",
            "cny": "🇨🇳 CNY - Yuan chinois",
            "inr": "🇮🇳 INR - Roupie indienne",
            "krw": "🇰🇷 KRW - Won sud-coréen",
            "mxn": "🇲🇽 MXN - Peso mexicain",
            "brl": "🇧🇷 BRL - Real brésilien",
            "rub": "🇷🇺 RUB - Rouble russe",
            "zar": "🇿🇦 ZAR - Rand sud-africain",
            "sgd": "🇸🇬 SGD - Dollar singapourien",
            "hkd": "🇭🇰 HKD - Dollar de Hong Kong",
            "nzd": "🇳🇿 NZD - Dollar néo-zélandais",
            "sek": "🇸🇪 SEK - Couronne suédoise",
            "nok": "🇳🇴 NOK - Couronne norvégienne",
            "dkk": "🇩🇰 DKK - Couronne danoise",
            "pln": "🇵🇱 PLN - Zloty polonais",
            "thb": "🇹🇭 THB - Baht thaïlandais",
            "try": "🇹🇷 TRY - Livre turque",
            "idr": "🇮🇩 IDR - Roupie indonésienne",
            "myr": "🇲🇾 MYR - Ringgit malaisien",
            "php": "🇵🇭 PHP - Peso philippin",
            "czk": "🇨🇿 CZK - Couronne tchèque",
            "ils": "🇮🇱 ILS - Shekel israélien",
            "clp": "🇨🇱 CLP - Peso chilien",
            "pkr": "🇵🇰 PKR - Roupie pakistanaise",
            "ars": "🇦🇷 ARS - Peso argentin",
            "aed": "🇦🇪 AED - Dirham des EAU",
            "sar": "🇸🇦 SAR - Riyal saoudien",
            "twd": "🇹🇼 TWD - Dollar taïwanais",
            "vnd": "🇻🇳 VND - Dong vietnamien",
            "ngn": "🇳🇬 NGN - Naira nigérian",
            "huf": "🇭🇺 HUF - Forint hongrois",
            "bdt": "🇧🇩 BDT - Taka bangladais",
            "egp": "🇪🇬 EGP - Livre égyptienne",
            "cop": "🇨🇴 COP - Peso colombien",
            "pen": "🇵🇪 PEN - Sol péruvien"
        }
        
        # RPC endpoint Solana - plusieurs options
        self.solana_rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana",
            "https://solana-mainnet.rpc.extrnode.com"
        ]
        self.current_rpc_index = 0
        self.solana_rpc = self.solana_rpc_endpoints[0]
        
        # Obtenir le taux de change
        self.get_exchange_rate()
        
        # Frame principal avec 2 colonnes
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurer les colonnes pour un ratio 50/50
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Colonne gauche - Formulaire (50%)
        left_frame = ttk.Frame(main_container, relief=tk.RIDGE, borderwidth=2)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Titre gauche
        ttk.Label(left_frame, text="Créer une facture", 
                 font=("Arial", 14, "bold")).pack(pady=15)
        
        # Frame pour le formulaire
        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill=tk.X, padx=20)
        
        # Montant et devise
        amount_currency_frame = ttk.Frame(form_frame)
        amount_currency_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Centrer le contenu
        center_frame = ttk.Frame(amount_currency_frame)
        center_frame.pack(anchor=tk.CENTER)
        
        ttk.Label(center_frame, text="Montant:", 
                 font=("Arial", 11)).pack(pady=(0, 5))
        
        entry_select_frame = ttk.Frame(center_frame)
        entry_select_frame.pack()
        
        # Champ montant (20 caractères)
        self.amount_entry = ttk.Entry(entry_select_frame, font=("Arial", 12), width=15, justify="right")
        self.amount_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.amount_entry.insert(0, "0.10")
        self.amount_entry.bind('<KeyRelease>', self.on_amount_change)
        
        # Liste déroulante des devises
        self.currency_var = tk.StringVar(value="cad")
        self.currency_combo = ttk.Combobox(
            entry_select_frame, 
            textvariable=self.currency_var,
            values=list(self.currencies.keys()),
            state='readonly',
            width=5,
            font=("Arial", 11)
        )
        self.currency_combo.pack(side=tk.LEFT)
        self.currency_combo.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # Label pour afficher le nom complet de la devise
        self.currency_name_label = ttk.Label(
            center_frame,
            text=self.currencies["cad"],
            font=("Arial", 9),
            foreground="gray"
        )
        self.currency_name_label.pack(pady=(3, 0))
        
        # Montant USDT (calculé) - centré
        usdt_center_frame = ttk.Frame(form_frame)
        usdt_center_frame.pack(fill=tk.X, pady=(15, 5))
        
        usdt_content_frame = ttk.Frame(usdt_center_frame)
        usdt_content_frame.pack(anchor=tk.CENTER)
        
        ttk.Label(usdt_content_frame, text="Montant (USDT):", 
                 font=("Arial", 11)).pack(pady=(0, 5))
        self.usdt_entry = ttk.Entry(usdt_content_frame, font=("Arial", 12), 
                                     state='readonly', width=20, justify="center")
        self.usdt_entry.pack()
        
        # Adresse Solana
        ttk.Label(form_frame, text="Adresse Solana:", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=(15, 5))
        self.address_entry = ttk.Entry(form_frame, font=("Arial", 10))
        self.address_entry.pack(fill=tk.X)
        
        # Clé API Helius (obligatoire)
        ttk.Label(form_frame, text="Clé API Helius (obligatoire):", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=(15, 5))
        self.helius_key_entry = ttk.Entry(form_frame, font=("Arial", 9), show="*")
        self.helius_key_entry.pack(fill=tk.X)
        self.helius_key_entry.bind('<KeyRelease>', self.update_rpc_endpoint)
        
        # Taux de change
        self.rate_label = ttk.Label(form_frame, 
                                    text=f"Taux: 1 USDT = {self.usdt_to_currency:.2f} {self.selected_currency.upper()}",
                                    font=("Arial", 9), foreground="gray")
        self.rate_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Bouton Générer
        self.generate_btn = ttk.Button(left_frame, 
                                       text="Générer QR Code de la facture", 
                                       command=self.generate_invoice)
        self.generate_btn.pack(pady=15)
        
        # Bouton Annuler (caché au départ)
        self.cancel_btn = ttk.Button(left_frame, 
                                     text="Annuler", 
                                     command=self.cancel_transaction)
        # Le bouton Annuler n'est pas empaqueté, donc invisible au départ
        
        # Zone QR Code (plus grande)
        self.qr_container = ttk.Frame(left_frame, relief=tk.SUNKEN, borderwidth=1)
        self.qr_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.qr_label = ttk.Label(self.qr_container, text="", anchor=tk.CENTER)
        self.qr_label.pack(expand=True, fill=tk.BOTH)
        
        # Colonne droite - Transactions (50%)
        right_frame = ttk.Frame(main_container, relief=tk.RIDGE, borderwidth=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Titre droite
        ttk.Label(right_frame, text="Liste des transactions", 
                 font=("Arial", 14, "bold")).pack(pady=15)
        
        # Bouton Sauvegarder
        self.save_btn = ttk.Button(right_frame, 
                                   text="💾 Sauvegarder les paiements", 
                                   command=self.save_payments)
        self.save_btn.pack(pady=(0, 10))
        
        # Liste des transactions
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.transaction_list = tk.Listbox(list_frame, 
                                          font=("Courier", 9),
                                          yscrollcommand=scrollbar.set)
        self.transaction_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.transaction_list.yview)
        
        # Liste pour stocker les paiements réussis
        self.successful_payments = []
        
        # Calculer USDT initial
        self.update_usdt()
        
    def get_exchange_rate(self):
        """Obtenir le taux de change USDT/devise sélectionnée"""
        try:
            # API gratuite pour obtenir les taux de change
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies={self.selected_currency}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.usdt_to_currency = data['tether'][self.selected_currency]
            else:
                self.usdt_to_currency = 1.0
        except:
            # Taux de secours si l'API ne répond pas
            self.usdt_to_currency = 1.38 if self.selected_currency == "cad" else 1.0
    
    def on_currency_change(self, event=None):
        """Appelé quand la devise change"""
        self.selected_currency = self.currency_var.get()
        
        # Mettre à jour le nom de la devise
        self.currency_name_label.config(text=self.currencies[self.selected_currency])
        
        # Obtenir le nouveau taux de change
        self.get_exchange_rate()
        
        # Mettre à jour l'affichage du taux
        helius_key = self.helius_key_entry.get().strip()
        if helius_key:
            self.rate_label.config(text=f"Taux: 1 USDT = {self.usdt_to_currency:.2f} {self.selected_currency.upper()} | RPC: Helius ⚡")
        else:
            self.rate_label.config(text=f"Taux: 1 USDT = {self.usdt_to_currency:.2f} {self.selected_currency.upper()}")
        
        # Recalculer le montant USDT
        self.update_usdt()
        
        # Arrêter le monitoring et effacer le QR
        self.monitoring = False
        self.qr_label.config(image='', text="")
        self.qr_label.image = None
        self.generate_btn.config(state='normal')
    
    def cancel_transaction(self):
        """Annuler la transaction en cours"""
        # Arrêter le monitoring
        self.monitoring = False
        
        # Effacer le QR code
        self.qr_label.config(image='', text="")
        self.qr_label.image = None
        
        # Cacher le bouton Annuler
        self.cancel_btn.pack_forget()
        
        # Réafficher le bouton Générer
        self.generate_btn.pack(pady=15, before=self.qr_container)
        
        # Message dans la liste
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transaction_list.insert(0, f"[{timestamp}] ❌ Transaction annulée")
    
    def on_amount_change(self, event=None):
        """Appelé quand le montant CAD change"""
        # Arrêter le monitoring
        self.monitoring = False
        
        # Effacer le QR code
        self.qr_label.config(image='', text="")
        self.qr_label.image = None
        
        # Réactiver le bouton
        self.generate_btn.config(state='normal')
        
        # Mettre à jour le montant USDT
        self.update_usdt()
            
    def update_usdt(self, event=None):
        """Mettre à jour le montant USDT basé sur la devise"""
        try:
            amount = float(self.amount_entry.get())
            usdt_amount = amount / self.usdt_to_currency
            
            self.usdt_entry.config(state='normal')
            self.usdt_entry.delete(0, tk.END)
            self.usdt_entry.insert(0, f"{usdt_amount:.2f}")
            self.usdt_entry.config(state='readonly')
        except:
            self.usdt_entry.config(state='normal')
            self.usdt_entry.delete(0, tk.END)
            self.usdt_entry.insert(0, "0.00")
            self.usdt_entry.config(state='readonly')
    
    def update_rpc_endpoint(self, event=None):
        """Mettre à jour l'endpoint RPC si une clé Helius est fournie"""
        helius_key = self.helius_key_entry.get().strip()
        if helius_key:
            self.solana_rpc = f"https://mainnet.helius-rpc.com/?api-key={helius_key}"
            self.rate_label.config(text=f"Taux: 1 USDT = {self.usdt_to_currency:.2f} {self.selected_currency.upper()} | RPC: Helius ⚡")
        else:
            self.solana_rpc = None
            self.rate_label.config(text=f"Taux: 1 USDT = {self.usdt_to_currency:.2f} {self.selected_currency.upper()} | ⚠ Clé Helius requise")
    
    def generate_invoice(self):
        """Générer la facture avec QR code"""
        try:
            amount = self.amount_entry.get().strip()
            usdt_amount = self.usdt_entry.get().strip()
            address = self.address_entry.get().strip()
            helius_key = self.helius_key_entry.get().strip()
            
            # Vérifier que la clé Helius est fournie
            if not helius_key:
                messagebox.showerror("Erreur", "La clé API Helius est obligatoire.\n\nObtenez-en une gratuitement sur:\nhttps://helius.dev")
                return
            
            if not amount or not address:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
                return
            
            # Validation
            try:
                float(amount)
                float(usdt_amount)
            except:
                messagebox.showerror("Erreur", "Montant invalide")
                return
            
            # Créer l'URL Solana Pay
            solana_url = f"solana:{address}?amount={usdt_amount}&spl-token={self.USDT_TOKEN}"
            
            # Générer le QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=3,
            )
            qr.add_data(solana_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((350, 350), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.qr_label.config(image=photo, text="")
            self.qr_label.image = photo
            
            # Cacher le bouton Générer et afficher le bouton Annuler
            self.generate_btn.pack_forget()
            self.cancel_btn.pack(pady=15, before=self.qr_container)
            
            # Obtenir le solde initial USDT
            self.initial_balance = self.get_usdt_balance(address)
            
            # Démarrer la surveillance de la transaction
            self.monitoring = True
            self.start_time = time.time()
            threading.Thread(target=self.monitor_transaction, 
                           args=(address, usdt_amount, amount), 
                           daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
    
    def get_usdt_balance(self, address):
        """Obtenir le solde USDT d'une adresse"""
        try:
            # Obtenir les comptes de tokens pour cette adresse
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    address,
                    {"mint": self.USDT_TOKEN},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            response = requests.post(
                self.solana_rpc,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if "result" not in data or not data["result"]["value"]:
                return 0.0  # Pas de compte USDT = solde 0
            
            # Récupérer le solde du premier compte USDT
            token_account = data["result"]["value"][0]
            balance = float(token_account["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"])
            
            return balance
            
        except Exception as e:
            print(f"Erreur get_usdt_balance: {e}")
            return None
    
    def monitor_transaction(self, address, usdt_amount, original_amount):
        """Surveiller si la transaction est complétée en vérifiant le solde"""
        timeout = 120  # 2 minutes
        check_interval = 3  # Vérifier toutes les 3 secondes
        
        def log_message(msg):
            def update():
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.transaction_list.insert(0, f"[{timestamp}] {msg}")
                if self.transaction_list.size() > 50:
                    self.transaction_list.delete(50, tk.END)
            self.root.after(0, update)
        
        if self.initial_balance is None:
            log_message("⚠ Impossible de lire le solde initial")
        else:
            log_message(f"💰 Solde initial: {self.initial_balance:.2f} USDT")
            log_message(f"🎯 En attente de: +{usdt_amount} USDT")
        
        last_logged_balance = self.initial_balance
        
        while self.monitoring and (time.time() - self.start_time) < timeout:
            # Obtenir le solde actuel
            current_balance = self.get_usdt_balance(address)
            
            if current_balance is not None and self.initial_balance is not None:
                difference = current_balance - self.initial_balance
                expected = float(usdt_amount)
                
                # N'afficher que si le solde a changé depuis le dernier log
                if current_balance != last_logged_balance:
                    log_message(f"💵 Solde actuel: {current_balance:.2f} USDT (Δ {difference:+.2f})")
                    last_logged_balance = current_balance
                
                # Vérifier si on a reçu le montant attendu (tolérance de 1%)
                tolerance = expected * 0.01
                if abs(difference - expected) <= tolerance and difference > 0:
                    log_message(f"✅ Paiement détecté: {difference:.2f} USDT!")
                    self.transaction_completed(True, original_amount, usdt_amount, address)
                    return
            
            time.sleep(check_interval)
        
        # Timeout après 2 minutes
        if self.monitoring:
            log_message("⏱️ Timeout - aucun paiement reçu")
            self.transaction_completed(False, original_amount, usdt_amount, address)
    
    def transaction_completed(self, success, original_amount, usdt_amount, address):
        """Afficher le résultat de la transaction"""
        self.monitoring = False
        
        def update_ui():
            if success:
                # Afficher "Merci beaucoup"
                self.qr_label.config(image='', 
                                    text="✓ Merci beaucoup!\n\nPaiement reçu",
                                    font=("Arial", 16, "bold"),
                                    foreground="green")
                
                # Ajouter à la liste
                timestamp = datetime.now().strftime("%Hh%M")
                currency_upper = self.selected_currency.upper()
                entry = f"{timestamp} -- {float(original_amount):.2f} {currency_upper} ({float(usdt_amount):.2f} USDT) reçu par {address[:4]}...{address[-4:]}"
                self.transaction_list.insert(0, entry)
                
                # Stocker le paiement réussi
                payment_record = {
                    'timestamp': timestamp,
                    'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'amount': float(original_amount),
                    'currency': currency_upper,
                    'usdt': float(usdt_amount),
                    'address': address,
                    'entry': entry
                }
                self.successful_payments.append(payment_record)
            else:
                # Afficher "Problème"
                self.qr_label.config(image='',
                                    text="✗ Problème\n\nAucun paiement reçu\n(timeout 2 min)",
                                    font=("Arial", 14, "bold"),
                                    foreground="red")
            
            # Cacher le bouton Annuler et réafficher le bouton Générer
            self.cancel_btn.pack_forget()
            self.generate_btn.pack(pady=15, before=self.qr_container)
        
        self.root.after(0, update_ui)
    
    def save_payments(self):
        """Sauvegarder tous les paiements réussis dans un fichier .txt"""
        if not self.successful_payments:
            messagebox.showinfo("Information", "Aucun paiement à sauvegarder.")
            return
        
        # Demander où sauvegarder le fichier
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            initialfile=f"paiements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not filename:
            return  # L'utilisateur a annulé
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("RAPPORT DES PAIEMENTS SOLANA - USDT\n")
                f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")
                
                total_usdt = 0
                
                # Inverser la liste pour avoir les paiements du plus ancien au plus récent
                for i, payment in enumerate(reversed(self.successful_payments), 1):
                    f.write(f"Paiement #{i}\n")
                    f.write(f"Date/Heure: {payment['datetime']}\n")
                    f.write(f"Montant: {payment['amount']:.2f} {payment['currency']}\n")
                    f.write(f"Équivalent: {payment['usdt']:.2f} USDT\n")
                    f.write(f"Adresse: {payment['address']}\n")
                    f.write("-" * 70 + "\n\n")
                    
                    total_usdt += payment['usdt']
                
                f.write("=" * 70 + "\n")
                f.write(f"TOTAL: {len(self.successful_payments)} paiement(s)\n")
                f.write(f"TOTAL EN USDT: {total_usdt:.2f} USDT\n")
                f.write("=" * 70 + "\n")
            
            messagebox.showinfo("Succès", 
                              f"Paiements sauvegardés!\n\n"
                              f"Fichier: {filename}\n"
                              f"Nombre de paiements: {len(self.successful_payments)}\n"
                              f"Total: {total_usdt:.2f} USDT")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SolanaPaymentSystem(root)
    root.mainloop()