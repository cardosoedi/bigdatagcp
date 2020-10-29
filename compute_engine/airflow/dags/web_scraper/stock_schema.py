import datetime


def get_stock_template():
    return {
        "papel": None,
        "empresa": None,
        "process_date": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "ult_balanco_processado": None,
        "tipo": None,
        "setor": None,
        "subsetor": None,
        "data_ult_cot": None,
        "cotacao": None,
        "min_52_sem": None,
        "max_52_sem": None,
        "nro_acoes": None,
        "vol_med_2m": None,
        "valor_de_mercado": None,
        "valor_da_firma": None,
        "oscilacoes_dia": None,
        "oscilacoes_mes": None,
        "oscilacoes_30_dias": None,
        "oscilacoes_12_meses": None,
        "oscilacoes_2020": None,
        "oscilacoes_2019": None,
        "oscilacoes_2018": None,
        "oscilacoes_2017": None,
        "oscilacoes_2016": None,
        "oscilacoes_2015": None,
        "indicadores_fundamentalistas_cres_rec_5a/5": None,
        "indicadores_fundamentalistas_ebit_ativo": None,
        "indicadores_fundamentalistas_ev_ebit": None,
        "indicadores_fundamentalistas_ev_ebitda": None,
        "indicadores_fundamentalistas_div_br_patrim": None,
        "indicadores_fundamentalistas_div_yield": None,
        "indicadores_fundamentalistas_giro_ativos": None,
        "indicadores_fundamentalistas_liquidez_corr": None,
        "indicadores_fundamentalistas_lpa": None,
        "indicadores_fundamentalistas_marg_bruta": None,
        "indicadores_fundamentalistas_marg_ebit": None,
        "indicadores_fundamentalistas_marg_liquida": None,
        "indicadores_fundamentalistas_pativos": None,
        "indicadores_fundamentalistas_pativ_circ_liq": None,
        "indicadores_fundamentalistas_pcap_giro": None,
        "indicadores_fundamentalistas_pebit": None,
        "indicadores_fundamentalistas_pl": None,
        "indicadores_fundamentalistas_psr": None,
        "indicadores_fundamentalistas_pvp": None,
        "indicadores_fundamentalistas_roe": None,
        "indicadores_fundamentalistas_roic": None,
        "indicadores_fundamentalistas_vpa": None,
        "balanco_patrimonial_ativo": None,
        "balanco_patrimonial_ativo_circulante": None,
        "balanco_patrimonial_cart_de_credito": None,
        "balanco_patrimonial_depositos": None,
        "balanco_patrimonial_disponibilidades": None,
        "balanco_patrimonial_div_bruta": None,
        "balanco_patrimonial_div_liquida": None,
        "balanco_patrimonial_patrim_liq": None,
        "ebit_ultimos_12_meses": None,
        "lucro_liquido_ultimos_12_meses": None,
        "rec_servicos_ultimos_12_meses": None,
        "receita_liquida_ultimos_12_meses": None,
        "result_int_financ_ultimos_12_meses": None,
        "ebit_ultimos_3_meses": None,
        "lucro_liquido_ultimos_3_meses": None,
        "rec_servicos_ultimos_3_meses": None,
        "receita_liquida_ultimos_3_meses": None,
        "result_int_financ_ultimos_3_meses": None}
