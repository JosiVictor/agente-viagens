import requests
from langchain_core.tools import tool
from src.config import REQUEST_TIMEOUT

WMO_CODES = {
    0: "céu limpo", 1: "predominantemente limpo", 2: "parcialmente nublado",
    3: "nublado", 45: "neblina", 48: "neblina com geada", 51: "garoa leve",
    53: "garoa", 55: "garoa forte", 61: "chuva fraca", 63: "chuva",
    65: "chuva forte", 71: "neve fraca", 73: "neve", 75: "neve forte",
    80: "pancadas de chuva", 81: "pancadas fortes", 82: "pancadas violentas",
    95: "tempestade", 96: "tempestade com granizo", 99: "tempestade forte com granizo",
}


def _get_json(url: str, params: dict) -> dict:
    """GET simples com timeout; levanta exceção se der erro HTTP."""
    resposta = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    resposta.raise_for_status()
    return resposta.json()


@tool
def previsao_do_tempo(cidade: str) -> str:
    """Retorna a previsão do tempo dos próximos 7 dias para uma cidade
    (temperatura mínima/máxima, chance de chuva e condição do céu).
    Use quando o usuário perguntar sobre clima ou melhor época/dia para viajar."""
    try:
        geo = _get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": cidade, "count": 1, "language": "pt"},
        )
        if not geo.get("results"):
            return f"Não encontrei a cidade '{cidade}'. Tente outro nome."
        local = geo["results"][0]
        dados = _get_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": local["latitude"],
                "longitude": local["longitude"],
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,"
                         "precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 7,
            },
        )
        d = dados["daily"]
        linhas = [f"Previsão para {local['name']} ({local.get('country', '')}):"]
        for i, dia in enumerate(d["time"]):
            cond = WMO_CODES.get(d["weathercode"][i], "condição variável")
            linhas.append(
                f"- {dia}: {d['temperature_2m_min'][i]}°C a "
                f"{d['temperature_2m_max'][i]}°C, chuva "
                f"{d['precipitation_probability_max'][i]}%, {cond}"
            )
        return "\n".join(linhas)
    except requests.RequestException as erro:
        return f"Erro ao consultar o clima: {erro}"
    except (KeyError, IndexError, ValueError) as erro:
        return f"Resposta inesperada do serviço de clima: {erro}"


@tool
def converter_moeda(valor: float, moeda_origem: str, moeda_destino: str) -> str:
    """Converte um valor entre moedas usando a cotação atual.
    Use códigos de 3 letras (BRL, USD, EUR, GBP, JPY...).
    Use quando o usuário quiser saber quanto custa algo em outra moeda."""
    origem, destino = moeda_origem.upper().strip(), moeda_destino.upper().strip()
    try:
        dados = _get_json(f"https://open.er-api.com/v6/latest/{origem}", {})
        if dados.get("result") != "success":
            return f"Moeda de origem inválida: {origem}"
        taxa = dados["rates"].get(destino)
        if taxa is None:
            return f"Moeda de destino inválida: {destino}"
        return (f"{valor:.2f} {origem} = {valor * taxa:.2f} {destino} "
                f"(cotação: 1 {origem} = {taxa:.4f} {destino})")
    except requests.RequestException as erro:
        return f"Erro ao consultar a cotação: {erro}"


@tool
def pesquisar_destino(consulta: str) -> str:
    """Busca na Wikipédia (em português) um resumo sobre um lugar, cidade ou
    ponto turístico: história, localização e características principais.
    Use quando o usuário quiser conhecer ou saber mais sobre um destino."""
    try:
        dados = _get_json(
            "https://pt.wikipedia.org/w/api.php",
            {
                "action": "query", "generator": "search", "gsrsearch": consulta,
                "gsrlimit": 1, "prop": "extracts", "exintro": 1,
                "explaintext": 1, "format": "json",
            },
        )
        paginas = dados.get("query", {}).get("pages", {})
        if not paginas:
            return f"Não encontrei informações sobre '{consulta}'."
        pagina = next(iter(paginas.values()))
        return f"{pagina['title']}: {pagina.get('extract', '')[:1200]}"
    except requests.RequestException as erro:
        return f"Erro ao pesquisar na Wikipédia: {erro}"


@tool
def calcular_orcamento(dias: int, custo_diario: float,
                       passagens: float = 0.0, outros: float = 0.0) -> str:
    """Calcula o orçamento total de uma viagem: dias x custo diário
    (hospedagem + alimentação + passeios) + passagens + outros gastos.
    Todos os valores devem estar na mesma moeda. Use para somar custos
    ao invés de inventar."""
    if dias <= 0 or custo_diario < 0 or passagens < 0 or outros < 0:
        return "Valores inválidos: dias deve ser > 0 e custos não podem ser negativos."
    gasto_diarias = dias * custo_diario
    total = gasto_diarias + passagens + outros
    return (f"Diárias: {dias} x {custo_diario:.2f} = {gasto_diarias:.2f}\n"
            f"Passagens: {passagens:.2f}\nOutros: {outros:.2f}\n"
            f"TOTAL: {total:.2f}")


FERRAMENTAS = [previsao_do_tempo, converter_moeda, pesquisar_destino, calcular_orcamento]