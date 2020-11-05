from datetime import datetime


class FieldsTreatment:
    @staticmethod
    def _date_fields(stock, field):
        date = datetime.strptime(stock[field], '%d/%m/%Y')
        stock[field] = date.strftime('%Y-%m-%d %H:%M:%S')
        return stock

    @staticmethod
    def _number_fields(stock, field_prefix):
        result = dict()
        for k, v in stock.items():
            if isinstance(v, str) and k.startswith(field_prefix) and len(v) > 0:
                if v.find('%') >= 0:
                    result[k] = float(v.replace('%', '').replace(',', '.'))
                else:
                    result[k] = float(v.replace(',', '.'))
            else:
                result[k] = v
        return result

    @staticmethod
    def _integer_fields(stock, field_prefix):
        result = dict()
        for k, v in stock.items():
            if isinstance(v, str) and k.startswith(field_prefix) and len(v) > 0:
                result[k] = int(v.replace(',', '.'))
            else:
                result[k] = v
        return result

    @staticmethod
    def _remove_hifen_values(stock):
        for k, v in stock.items():
            if v == '-':
                stock[k] = None
        return stock

    @staticmethod
    def _rename_percent_fields(stock):
        field_names = ['indicadores_fundamentalistas_cres_rec_5a',
                       'indicadores_fundamentalistas_div_yield',
                       'indicadores_fundamentalistas_ebit_ativo',
                       'indicadores_fundamentalistas_marg_bruta',
                       'indicadores_fundamentalistas_marg_ebit',
                       'indicadores_fundamentalistas_marg_liquida',
                       'indicadores_fundamentalistas_roe',
                       'indicadores_fundamentalistas_roic',
                       'oscilacoes_12_meses',
                       'oscilacoes_2012',
                       'oscilacoes_2013',
                       'oscilacoes_2014',
                       'oscilacoes_2015',
                       'oscilacoes_2016',
                       'oscilacoes_2017',
                       'oscilacoes_2018',
                       'oscilacoes_2019',
                       'oscilacoes_2020',
                       'oscilacoes_30_dias',
                       'oscilacoes_dia',
                       'oscilacoes_mes']
        for name in field_names:
            stock[name + "_perc"] = stock.pop(name)
        return stock

    @classmethod
    def treat_all_fields(cls, stock):
        num_fields = ['cotacao',
                      'min_52_sem',
                      'max_52_sem',
                      'indicadores_fundamentalistas',
                      'oscilacoes']

        int_fields = ['nro_acoes',
                      'vol_med_2m',
                      'valor',
                      'result_int',
                      'rec_servicos',
                      'ebit_ultimos',
                      'receita_liquida',
                      'lucro_liquido',
                      'balanco_patrimonial']

        stock = cls._remove_hifen_values(stock)
        stock = cls._date_fields(stock, 'ult_balanco_processado')
        stock = cls._date_fields(stock, 'data_ult_cot')
        for field in int_fields:
            stock = cls._integer_fields(stock, field)
        for field in num_fields:
            stock = cls._number_fields(stock, field)
        stock = cls._rename_percent_fields(stock)
        return stock
