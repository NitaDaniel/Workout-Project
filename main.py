import tkinter as tk
from tkinter import messagebox
import time
from pushbullet import Pushbullet
from PIL import Image, ImageTk


# Pushbullet API Key
PUSHBULLET_API_KEY = "your API key"
pb = Pushbullet(PUSHBULLET_API_KEY)

# Trimite notificare Pushbullet
def trimite_notificare_pushbullet(mesaj):
    push = pb.push_note("Antrenament Terminat", mesaj)
    print("Notificare trimisă pe telefon!")

# Variabile globale
echipamente_selectate = []
nivel_fitness_selectat = 'incepator'
tip_antrenament_selectat = 'forță'
intensitate_selectata = 'medie'
plan_antrenament_final = []
exercitii_personalizate = []  # Lista pentru exercițiile personalizate

# Timpuri pentru cronometrare
start_timp_antrenament = None
start_timp_exercitiu = None

# Determinarea numărului de repetări
def determina_repetari(nivel_fitness, intensitate):
    baza = {'incepator': 10, 'intermediar': 15, 'avansat': 20}.get(nivel_fitness, 10)
    ajustare = {'scăzută': -2, 'medie': 0, 'ridicată': 3}.get(intensitate, 0)
    return max(1, baza + ajustare)

# Generare antrenament
def genereaza_antrenament(echipamente, nivel_fitness, durata, tip_antrenament, intensitate):
    exercitii = {
        'forță': {
            'gantere': ['Deadlift cu gantere', 'Presă umeri', 'Ramat cu gantere'],
            'benzi': ['Îndreptări cu bandă', 'Ramat cu bandă', 'Presă piept bandă'],
            'niciunul': ['Flotări', 'Ghemuiri', 'Fandări']
        },
        'cardio': {
            'gantere': ['Clean and press', 'Snatch alternant', 'Swing cu gantere'],
            'benzi': ['Jumping jacks cu bandă', 'Sprint pe loc cu bandă', 'Burpees cu bandă'],
            'niciunul': ['Burpees', 'Jumping jacks', 'High knees']
        },
        'mobilitate': {
            'gantere': ['Rotiri cu gantere ușoare', 'Întinderi dinamice'],
            'benzi': ['Stretching umăr cu bandă', 'Extensii spate'],
            'niciunul': ['Cercuri de brațe', 'Aplecări laterale', 'Rotiri trunchi']
        },
        'combinație': {
            'gantere': ['Thruster cu gantere', 'Burpee + Presă'],
            'benzi': ['Ghemuiri + Presă bandă', 'Lunge + Tracțiune bandă'],
            'niciunul': ['Jump squat', 'Mountain climbers', 'Flotări + ridicări']
        }
    }

    repetari = determina_repetari(nivel_fitness, intensitate)
    plan = f"Tip antrenament: {tip_antrenament}\nIntensitate: {intensitate}\nNivel: {nivel_fitness}\nDurata: {durata} min\nEchipamente: {', '.join(echipamente)}\n\n"
    exercitii_pentru_timp = []
    total_ex = len(echipamente) * 3
    durata_ex = max(1, int(durata / total_ex))

    for echip in echipamente:
        lista = exercitii.get(tip_antrenament, {}).get(echip, [])
        if lista:
            plan += f"--- Cu {echip} ---\n"
            for ex in lista:
                plan += f"- {ex}: {repetari} rep. / {durata_ex} min\n"
                exercitii_pentru_timp.append((ex, durata_ex))
            plan += "\n"

    global plan_antrenament_final
    plan_antrenament_final = exercitii_pentru_timp
    return plan

# Adăugare exercițiu
def adauga_exercitiu_in_plan():
    f = tk.Toplevel(root)
    f.title("Adaugă Exercițiu")
    tk.Label(f, text="Nume exercițiu:").pack()
    e = tk.Entry(f)
    e.pack()

    def salveaza():
        if e.get():
            nume_ex = e.get().strip()
            exercitii_personalizate.append((nume_ex, 10))  # 1 min default
            plan_antrenament_final.append((nume_ex, 10))
            e.delete(0, tk.END)
            f.destroy()
            afiseaza_plan_antrenament()  # Regenerează eticheta cu tot

    tk.Button(f, text="Adaugă", command=salveaza).pack()

# Setări utilizator
def deschide_fereastra_setari():
    f = tk.Toplevel(root)
    f.title("Setări")
    optiuni = ['niciunul', 'gantere', 'benzi']
    echip_vars = {opt: tk.BooleanVar() for opt in optiuni}
    tk.Label(f, text="Echipamente:").pack()
    for opt in optiuni:
        tk.Checkbutton(f, text=opt.capitalize(), variable=echip_vars[opt]).pack(anchor='w')

    echip_custom = []
    e_custom = tk.Entry(f)
    e_custom.pack()
    def adauga_custom():
        val = e_custom.get().strip()
        if val:
            echip_custom.append(val.lower())
            l.insert(tk.END, val)
            e_custom.delete(0, tk.END)
    tk.Button(f, text="Adaugă Echipament", command=adauga_custom).pack()
    l = tk.Listbox(f, height=4)
    l.pack()

    nivel = tk.StringVar(value='incepator')
    tip = tk.StringVar(value='forță')
    intensitate = tk.StringVar(value='medie')
    for text, var, optiuni in [
        ("Nivel Fitness:", nivel, ['incepator', 'intermediar', 'avansat']),
        ("Tip Antrenament:", tip, ['forță', 'cardio', 'mobilitate', 'combinație']),
        ("Intensitate:", intensitate, ['scăzută', 'medie', 'ridicată'])
    ]:
        tk.Label(f, text=text).pack()
        tk.OptionMenu(f, var, *optiuni).pack()

    def salveaza():
        global echipamente_selectate, nivel_fitness_selectat, tip_antrenament_selectat, intensitate_selectata
        echipamente_selectate = [opt for opt, var in echip_vars.items() if var.get()] + echip_custom
        nivel_fitness_selectat = nivel.get()
        tip_antrenament_selectat = tip.get()
        intensitate_selectata = intensitate.get()
        f.destroy()
    tk.Button(f, text="Salvează", command=salveaza).pack(pady=10)

# Start / Stop cu cronometrare
def start_antrenament():
    global start_timp_antrenament
    start_timp_antrenament = time.time()
    status_label.config(text="Antrenament pornit!")

def stop_antrenament():
    global start_timp_antrenament
    if start_timp_antrenament:
        durata = int(time.time() - start_timp_antrenament)
        status_label.config(text=f"Antrenament oprit! Durata: {durata} sec.")
        start_timp_antrenament = None

        mesaj = f"✅ Antrenamentul tău s-a încheiat!\nDurată: {durata} secunde."
        trimite_notificare_pushbullet(mesaj)  # Trimite notificarea push
    else:
        status_label.config(text="Antrenamentul nu a fost pornit.")

def start_exercitiu():
    global start_timp_exercitiu
    start_timp_exercitiu = time.time()
    status_label.config(text="Exercițiu pornit!")

def stop_exercitiu():
    global start_timp_exercitiu
    if start_timp_exercitiu:
        durata = int(time.time() - start_timp_exercitiu)
        status_label.config(text=f"Exercițiu oprit! Durata: {durata} sec.")
        start_timp_exercitiu = None
    else:
        status_label.config(text="Exercițiul nu a fost pornit.")

# Generare plan
def afiseaza_plan_antrenament():
    try:
        durata = int(durata_entry.get())
    except ValueError:
        messagebox.showerror("Eroare", "Durata trebuie să fie un număr.")
        return

    plan = genereaza_antrenament(
        echipamente_selectate,
        nivel_fitness_selectat,
        durata,
        tip_antrenament_selectat,
        intensitate_selectata
    )

    # Adaugă exercițiile personalizate la finalul planului
    if exercitii_personalizate:
        plan += "--- Exerciții Adăugate Manual ---\n"
        for ex, durata_ex in exercitii_personalizate:
            plan += f"- {ex}: {durata_ex} min\n"
        plan += "\n"

    eticheta_antrenament.config(text=plan)

# Interfață principală
root = tk.Tk()
root.title("Antrenament Personalizat")
root.state('zoomed')


#imaginea de fundal
#bg_img = Image
#bg_img = bg_img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
#bg_photo = ImageTk.PhotoImage(bg_img)

# Plasează imaginea pe fundal
#background_label = tk.Label(root, image=bg_photo)
#background_label.place(x=0, y=0, relwidth=1, relheight=1)
#background_label.image = bg_photo

# Creează un container central
main_frame = tk.Frame(root)
main_frame.place(relx=0.5, rely=0.5, anchor='center')


tk.Label(main_frame, text="Configurează preferințele de antrenament:", font=("Arial", 9, "italic")).pack()
tk.Button(main_frame, text="Setări Utilizator", font=("Arial", 12), command=deschide_fereastra_setari).pack(pady=5)

tk.Label(main_frame, text="Adaugă manual un exercițiu la planul tău:", font=("Arial", 9, "italic")).pack()
tk.Button(main_frame, text="Adaugă Exercițiu la Plan", font=("Arial", 12), command=adauga_exercitiu_in_plan).pack(pady=5)


tk.Label(main_frame, text="Durata (minute):", font=("Arial", 12)).pack()
durata_entry = tk.Entry(main_frame)
durata_entry.pack(pady=5)

tk.Label(main_frame, text="Generează un plan de antrenament pe baza setărilor:", font=("Arial", 9, "italic")).pack()
tk.Button(main_frame, text="Generează Antrenament", font=("Arial", 12), command=afiseaza_plan_antrenament).pack(pady=10)

eticheta_antrenament = tk.Label(main_frame, text="", font=("Arial", 11), justify=tk.LEFT, anchor="center")
eticheta_antrenament.pack(pady=20)

status_label = tk.Label(main_frame, text="", font=("Arial", 12))
status_label.pack(pady=20)

tk.Button(main_frame, text="Start Antrenament", font=("Arial", 12), command=start_antrenament).pack()
tk.Button(main_frame, text="Stop Antrenament", font=("Arial", 12), command=stop_antrenament).pack()
tk.Button(main_frame, text="Start Exercițiu", font=("Arial", 12), command=start_exercitiu).pack()
tk.Button(main_frame, text="Stop Exercițiu", font=("Arial", 12), command=stop_exercitiu).pack()

root.mainloop()
