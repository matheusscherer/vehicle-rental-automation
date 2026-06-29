# vehicle_rental_automation.py
# Automação do processo de Locação de Veículo
# Projeto: Automação Inteligente para Negócios — Senac Tech Porto Alegre RS
# Autor: Matheus Scherer | @mtscfit
# Data: 22/06/2026

from datetime import date, datetime

# ─────────────────────────────────────────────
# DADOS SIMULADOS — frota e clientes
# ─────────────────────────────────────────────

# Simulação da frota de veículos disponíveis na locadora
VEHICLE_FLEET = {
    "ABC-1234": {"model": "Toyota Corolla", "category": "B", "available": True,  "daily_rate": 180.00},
    "DEF-5678": {"model": "Jeep Compass",   "category": "C", "available": False, "daily_rate": 320.00},
    "GHI-9012": {"model": "Fiat Mobi",      "category": "A", "available": True,  "daily_rate": 95.00},
}

# Categorias de CNH aceitas para cada categoria de veículo
ALLOWED_CNH_CATEGORIES = {
    "A": ["A", "AB"],           # motos
    "B": ["B", "AB", "C", "D", "E"],  # carros passeio
    "C": ["C", "D", "E"],       # utilitários
}

# Campos obrigatórios para validação do formulário de locação
REQUIRED_FIELDS = ["customer_name", "cnh_number", "cnh_category", "cnh_expiry", "plate", "rental_days"]


# ─────────────────────────────────────────────
# FUNÇÕES DE ENTRADA (INPUT)
# ─────────────────────────────────────────────

def collect_rental_data() -> dict:
    """
    [ENTRADA] Solicita e verifica a CNH válida do cliente
    e os dados necessários para iniciar a locação.
    """
    print("\n" + "=" * 55)
    print("      FORMULÁRIO DE LOCAÇÃO DE VEÍCULO")
    print("=" * 55)

    # Coleta os dados do cliente e da locação via terminal
    customer_name = input("Nome completo do cliente:          ").strip()
    cnh_number    = input("Número da CNH:                     ").strip()
    cnh_category  = input("Categoria da CNH (ex: B, AB, C):   ").strip().upper()
    cnh_expiry    = input("Validade da CNH (DD/MM/AAAA):      ").strip()
    plate         = input("Placa do veículo desejado:         ").strip().upper()
    rental_days   = input("Quantidade de dias de locação:     ").strip()

    # Retorna todos os dados coletados como dicionário
    return {
        "customer_name": customer_name,
        "cnh_number":    cnh_number,
        "cnh_category":  cnh_category,
        "cnh_expiry":    cnh_expiry,
        "plate":         plate,
        "rental_days":   rental_days,
    }


def request_credit_card() -> str:
    """
    [ENTRADA] Solicita o cartão de crédito do cliente para
    realizar o bloqueio do valor de caução.
    """
    print("\n[💳] Informe os dados do cartão para bloqueio da caução.")
    card_number = input("Número do cartão (apenas os 4 últimos dígitos): ").strip()
    return card_number


# ─────────────────────────────────────────────
# FUNÇÕES DE PROCESSAMENTO (PROCESSING)
# ─────────────────────────────────────────────

def validate_required_fields(rental_data: dict) -> bool:
    """
    [PROCESSAMENTO] Verifica se todos os campos obrigatórios
    foram preenchidos antes de prosseguir.
    """
    print("\n[🔍] Validando campos obrigatórios...")

    # for: percorre cada campo obrigatório verificando preenchimento
    for field in REQUIRED_FIELDS:
        if not rental_data.get(field):
            print(f"[ERRO] Campo obrigatório não preenchido: '{field}'")
            return False

    print("[✔] Todos os campos preenchidos.")
    return True


def validate_cnh(cnh_expiry: str, cnh_category: str, vehicle_category: str) -> bool:
    """
    [PROCESSAMENTO] Valida a CNH do cliente:
    - Verifica se está dentro do prazo de validade
    - Verifica se a categoria habilitada cobre o veículo escolhido
    """
    print("\n[🔍] Validando CNH...")

    # Converte a data de validade da CNH para objeto date
    try:
        expiry_date = datetime.strptime(cnh_expiry, "%d/%m/%Y").date()
    except ValueError:
        print("[ERRO] Formato de data inválido. Use DD/MM/AAAA.")
        return False

    # Verifica se a CNH não está vencida
    if expiry_date < date.today():
        print(f"[ERRO] CNH vencida em {cnh_expiry}. Locação não autorizada.")
        return False

    # Verifica se a categoria da CNH permite conduzir o veículo escolhido
    allowed = ALLOWED_CNH_CATEGORIES.get(vehicle_category, [])
    if cnh_category not in allowed:
        print(f"[ERRO] CNH categoria '{cnh_category}' não autorizada para veículo categoria '{vehicle_category}'.")
        return False

    print(f"[✔] CNH válida até {cnh_expiry} e categoria autorizada.")
    return True


def process_security_deposit(card_number: str, vehicle: dict, rental_days: int) -> dict:
    """
    [PROCESSAMENTO] Processa a autorização da caução junto à operadora
    do cartão e verifica a disponibilidade do veículo escolhido.
    """
    print("\n[💳] Processando caução e verificando disponibilidade...")

    # Verifica se o veículo está disponível na frota
    if not vehicle["available"]:
        print(f"[ERRO] Veículo {vehicle['model']} indisponível no momento.")
        return {}

    # Calcula os valores da locação e da caução (equivalente a 3 diárias)
    total_value   = vehicle["daily_rate"] * rental_days
    deposit_value = vehicle["daily_rate"] * 3

    print(f"[✔] Veículo disponível: {vehicle['model']}")
    print(f"[✔] Caução de R$ {deposit_value:.2f} bloqueada no cartão final {card_number}.")
    print(f"[✔] Total da locação: R$ {total_value:.2f} ({rental_days} dias × R$ {vehicle['daily_rate']:.2f})")

    # Retorna o resumo financeiro da locação
    return {"deposit": deposit_value, "total": total_value}


def generate_rental_contract(rental_data: dict, vehicle: dict, financials: dict) -> dict:
    """
    [PROCESSAMENTO] Gera o contrato de locação com dados do cliente,
    regras de devolução, seguros e valores.
    """
    print("\n[📄] Gerando contrato de locação...")

    # Monta o contrato como dicionário com todos os dados relevantes
    contract = {
        "customer_name":  rental_data["customer_name"],
        "cnh_number":     rental_data["cnh_number"],
        "vehicle_model":  vehicle["model"],
        "vehicle_plate":  rental_data["plate"],
        "rental_days":    int(rental_data["rental_days"]),
        "issue_date":     date.today().strftime("%d/%m/%Y"),
        "total_value":    financials["total"],
        "deposit_value":  financials["deposit"],
        "return_rules":   "Devolução no mesmo estado, com tanque cheio.",
        "insurance":      "Seguro básico incluído. Danos por negligência não cobertos.",
    }

    print("[✔] Contrato gerado com sucesso.")
    return contract


def collect_signature(customer_name: str) -> bool:
    """
    [PROCESSAMENTO] Coleta a assinatura digital do cliente no contrato.
    """
    print(f"\n[✍️ ] Contrato pronto para assinatura.")
    signature = input(f"Digite seu nome completo para assinar digitalmente: ").strip()

    # Verifica se o nome digitado corresponde ao nome do cliente
    if signature.lower() != customer_name.lower():
        print("[ERRO] Assinatura não confere com o nome do cliente.")
        return False

    print("[✔] Contrato assinado digitalmente.")
    return True


def vehicle_inspection(plate: str) -> list:
    """
    [PROCESSAMENTO] Realiza o checklist/vistoria do veículo junto
    com o cliente para anotar avarias pré-existentes.
    """
    print("\n[🔎] Iniciando vistoria do veículo...")

    # Lista de itens verificados na vistoria
    inspection_items = ["Lataria", "Vidros", "Pneus", "Faróis", "Interior", "Tanque"]
    inspection_report = []

    # for: percorre cada item do checklist de vistoria
    for item in inspection_items:
        status = input(f"  {item} — avaria? (s/n): ").strip().lower()

        # Registra avaria apenas se o cliente confirmar
        if status == "s":
            detail = input(f"  Descreva a avaria em '{item}': ").strip()
            inspection_report.append(f"{item}: {detail}")
        else:
            inspection_report.append(f"{item}: OK")

    print("[✔] Vistoria concluída e registrada.")
    return inspection_report


# ─────────────────────────────────────────────
# FUNÇÃO DE SAÍDA (OUTPUT)
# ─────────────────────────────────────────────

def deliver_vehicle(contract: dict, inspection_report: list) -> None:
    """
    [SAÍDA] Entrega as chaves, o documento do carro e libera
    o veículo para o cliente.
    """
    print("\n" + "=" * 55)
    print("        🚗 VEÍCULO LIBERADO PARA LOCAÇÃO")
    print("=" * 55)
    print(f"  Cliente:        {contract['customer_name']}")
    print(f"  CNH:            {contract['cnh_number']}")
    print(f"  Veículo:        {contract['vehicle_model']}")
    print(f"  Placa:          {contract['vehicle_plate']}")
    print(f"  Período:        {contract['rental_days']} dias")
    print(f"  Data de saída:  {contract['issue_date']}")
    print(f"  Total:          R$ {contract['total_value']:.2f}")
    print(f"  Caução:         R$ {contract['deposit_value']:.2f} bloqueada")
    print(f"  Seguro:         {contract['insurance']}")
    print(f"  Devolução:      {contract['return_rules']}")
    print("-" * 55)
    print("  VISTORIA INICIAL:")

    # for: percorre e exibe cada item registrado na vistoria
    for item in inspection_report:
        print(f"    • {item}")

    print("=" * 55)
    print("  ✅ Chaves e documento entregues. Boa viagem!")
    print("=" * 55)


# ─────────────────────────────────────────────
# FLUXO PRINCIPAL — LOOP WHILE COM ELSE
# ─────────────────────────────────────────────

def main():
    """
    Fluxo principal da automação de locação de veículo.
    Utiliza while para permitir novas tentativas, for para
    validação e vistoria, e else para encerramento limpo.
    """
    print("\n🚗 SISTEMA DE LOCAÇÃO DE VEÍCULO — SENAC TECH")

    max_attempts = 3   # número máximo de tentativas permitidas
    attempt = 0

    # while: mantém o sistema ativo enquanto houver tentativas disponíveis
    while attempt < max_attempts:
        attempt += 1
        print(f"\n[Tentativa {attempt} de {max_attempts}]")

        # ETAPA 1 — Entrada: coleta dados do cliente e da CNH
        rental_data = collect_rental_data()

        # ETAPA 2 — Processamento: valida campos obrigatórios
        if not validate_required_fields(rental_data):
            retry = input("\nDeseja corrigir os dados? (s/n): ").strip().lower()
            if retry != "s":
                break
            continue  # volta ao início do loop para nova tentativa

        # Busca o veículo na frota pelo número da placa
        vehicle = VEHICLE_FLEET.get(rental_data["plate"])
        if not vehicle:
            print(f"[ERRO] Placa '{rental_data['plate']}' não encontrada na frota.")
            retry = input("Deseja tentar com outra placa? (s/n): ").strip().lower()
            if retry != "s":
                break
            continue

        # ETAPA 3 — Processamento: valida CNH (validade e categoria)
        if not validate_cnh(rental_data["cnh_expiry"], rental_data["cnh_category"], vehicle["category"]):
            retry = input("\nDeseja corrigir os dados da CNH? (s/n): ").strip().lower()
            if retry != "s":
                break
            continue

        # ETAPA 4 — Entrada: solicita cartão para bloqueio da caução
        card_number = request_credit_card()

        # ETAPA 5 — Processamento: processa caução e verifica disponibilidade
        financials = process_security_deposit(card_number, vehicle, int(rental_data["rental_days"]))
        if not financials:
            retry = input("\nDeseja escolher outro veículo? (s/n): ").strip().lower()
            if retry != "s":
                break
            continue

        # ETAPA 6 — Processamento: gera contrato de locação
        contract = generate_rental_contract(rental_data, vehicle, financials)

        # ETAPA 7 — Processamento: coleta assinatura digital do cliente
        if not collect_signature(rental_data["customer_name"]):
            retry = input("\nDeseja assinar novamente? (s/n): ").strip().lower()
            if retry != "s":
                break
            continue

        # ETAPA 8 — Processamento: realiza vistoria do veículo
        inspection_report = vehicle_inspection(rental_data["plate"])

        # ETAPA 9 — Saída: entrega as chaves e libera o veículo
        deliver_vehicle(contract, inspection_report)

        # Marca o veículo como indisponível após a locação ser confirmada
        VEHICLE_FLEET[rental_data["plate"]]["available"] = False

        break  # locação concluída com sucesso — encerra o while

    else:
        # else do while: executado apenas se o loop terminar SEM um break
        # ou seja, quando o número máximo de tentativas foi esgotado
        print("\n[⚠️ ] Número máximo de tentativas atingido. Locação não realizada.")

    print("\n[Sistema encerrado. Obrigado!]\n")


# Ponto de entrada do script
if __name__ == "__main__":
    main()
