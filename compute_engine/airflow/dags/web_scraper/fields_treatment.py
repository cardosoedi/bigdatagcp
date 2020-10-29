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
            if isinstance(v, str) and k.startswith(field_prefix):
                if v.find('%') >= 0:
                    result[k + '%'] = float(v.replace('%', '').replace(',', '.'))
                else:
                    result[k] = float(v.replace(',', '.'))
            else:
                result[k] = v
        return result

    @staticmethod
    def _integer_fields(stock, field_prefix):
        result = dict()
        for k, v in stock.items():
            if isinstance(v, str) and k.startswith(field_prefix):
                result[k] = int(v.replace(',', '.'))
            else:
                result[k] = v
        return result

    def treat_all_fields(self, stock):
        num_fields = ['cotacao',
                      'min_52_sem',
                      'max_52_sem',
                      'nro_acoes',
                      'vol_med_2m',
                      'valor',
                      'result_int',
                      'rec_servicos',
                      'ebit_ultimos',
                      'receita_liquida',
                      'lucro_liquido',
                      'indicadores_fundamentalistas',
                      'oscilacoes',
                      'balanco_patrimonial']

        int_fields = ['nro_acoes',
                      'vol_med_2m',
                      'valor',
                      'result_int',
                      'rec_servicos',
                      'ebit_ultimos',
                      'receita_liquida',
                      'lucro_liquido',
                      'balanco_patrimonial']

        stock = self._date_fields(stock, 'ult_balanco_processado')
        stock = self._date_fields(stock, 'data_ult_cot')
        for field in int_fields:
            stock = self._integer_fields(stock, field)
        for field in num_fields:
            stock = self._number_fields(stock, field)
        return stock
