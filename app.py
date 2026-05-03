# Модель: Теорія масового обслуговування (Модель M/M/m)
# Автор: Сурков Максим Сергійович, група АІ-233   

from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def calculate_erlang_c(lam, mu, m):
    """Обчислює ймовірність черги за формулою Ерланга С.""" 
    rho = lam / (m * mu) 
    if rho >= 1: 
        return "Система перевантажена" 

    # Обчислення P0   
    sum_p = sum(((m * rho)**i) / math.factorial(i) for i in range(m)) 
    p0_inv = sum_p + (((m * rho)**m) / math.factorial(m)) * (1 / (1 - rho)) 
    p0 = 1 / p0_inv 

    # Обчислення ймовірності очікування (P_q)   
    p_q = (((m * rho)**m) / math.factorial(m)) * (1 / (1 - rho)) * p0 
    return p_q 

# Змінили метод на POST
@app.route('/calculate', methods=['POST'])
def calculate():
    # Отримуємо JSON з тіла запиту
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Очікується JSON формат даних у тілі запиту."}), 400

    try:
        # Беремо дані з JSON, якщо їх немає - залишаємо дефолтні значення
        lam = float(data.get('lam', 1800))
        mu = float(data.get('mu', 100))
        m = int(data.get('m', 20))
    except (ValueError, TypeError):
        return jsonify({"error": "Некоректний формат параметрів. Очікуються числа."}), 400

    rho = lam / (m * mu)
    p_q = calculate_erlang_c(lam, mu, m)

    # Обробка випадку перевантаження системи
    if p_q == "Система перевантажена":
        return jsonify({
            "input": {"lam": lam, "mu": mu, "m": m},
            "error": "Система перевантажена",
            "rho": round(rho, 3)
        })

    # Розрахунок метрик   
    w_q = p_q / (m * mu - lam) 
    w = w_q + (1 / mu) 

    # Повернення результату у форматі JSON
    return jsonify({
        "input": {
            "lam": lam,
            "mu": mu,
            "m": m
        },
        "result": {
            "rho": round(rho, 3),
            "p_q": round(p_q, 3),
            "w_q_ms": round(w_q * 1000, 3),
            "w_ms": round(w * 1000, 3)
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)