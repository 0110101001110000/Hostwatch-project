import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
import json
import numpy as np
from src.utils.logger import logger
import os

class DataWarehouseAnalyzer:
    def __init__(self, config_file="configs/db_config.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.connection = None
    
    def connect(self):
        """Conectar ao Data Warehouse"""
        try:
            self.connection = psycopg2.connect(**self.config)
            logger.info("Conectado ao Data Warehouse")
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise
    
    def get_price_by_city(self):
        """Consultar preço médio por cidade"""
        query = """
        SELECT 
            dl.cidade,
            dl.pais,
            COUNT(*) as total_hoteis,
            AVG(fh.preco) as preco_medio,
            MIN(fh.preco) as preco_minimo,
            MAX(fh.preco) as preco_maximo,
            AVG(fh.avaliacao) as avaliacao_media
        FROM fato_hospedagem fh
        JOIN dim_localizacao dl ON fh.sk_local = dl.sk_local
        GROUP BY dl.cidade, dl.pais
        ORDER BY preco_medio DESC
        """
        
        df = pd.read_sql(query, self.connection)
        logger.info(f"Consultados dados de {len(df)} cidades")
        logger.info(f"Cidades encontradas: {df['cidade'].tolist()}")
        return df
    
    def get_hotels_by_rating(self):
        """Consultar hotéis por faixa de avaliação"""
        query = """
        SELECT 
            CASE 
                WHEN fh.avaliacao >= 9.0 THEN 'Excelente (9.0+)'
                WHEN fh.avaliacao >= 8.0 THEN 'Muito Bom (8.0-8.9)'
                WHEN fh.avaliacao >= 7.0 THEN 'Bom (7.0-7.9)'
                WHEN fh.avaliacao >= 6.0 THEN 'Regular (6.0-6.9)'
                ELSE 'Ruim (< 6.0)'
            END as faixa_avaliacao,
            COUNT(*) as quantidade_hoteis,
            AVG(fh.preco) as preco_medio
        FROM fato_hospedagem fh
        WHERE fh.avaliacao > 0
        GROUP BY 
            CASE 
                WHEN fh.avaliacao >= 9.0 THEN 'Excelente (9.0+)'
                WHEN fh.avaliacao >= 8.0 THEN 'Muito Bom (8.0-8.9)'
                WHEN fh.avaliacao >= 7.0 THEN 'Bom (7.0-7.9)'
                WHEN fh.avaliacao >= 6.0 THEN 'Regular (6.0-6.9)'
                ELSE 'Ruim (< 6.0)'
            END
        ORDER BY preco_medio DESC
        """
        
        df = pd.read_sql(query, self.connection)
        return df
    
    def get_price_distribution(self):
        """Consultar distribuição de preços"""
        query = """
        SELECT 
            fh.preco,
            fh.avaliacao,
            dl.cidade,
            dl.pais,
            dh.nome as hotel_nome
        FROM fato_hospedagem fh
        JOIN dim_localizacao dl ON fh.sk_local = dl.sk_local
        JOIN dim_hotel dh ON fh.sk_hotel = dh.sk_hotel
        ORDER BY fh.preco
        """
        
        df = pd.read_sql(query, self.connection)
        return df
    
    def get_rating_analysis(self):
        """Consultar análise de avaliações por hotel"""
        query = """
        SELECT 
            dh.nome as hotel_nome,
            dl.cidade,
            dl.pais,
            fh.avaliacao,
            fh.preco,
            COUNT(*) OVER (PARTITION BY dl.cidade) as total_hoteis_cidade
        FROM fato_hospedagem fh
        JOIN dim_localizacao dl ON fh.sk_local = dl.sk_local
        JOIN dim_hotel dh ON fh.sk_hotel = dh.sk_hotel
        WHERE fh.avaliacao > 0
        ORDER BY fh.avaliacao DESC
        """
        
        df = pd.read_sql(query, self.connection)
        return df
    
    def get_top_hotels_by_city(self, top_n=5):
        """Consultar top N melhores hotéis por cidade"""
        query = """
        WITH ranked_hotels AS (
            SELECT 
                dh.nome as hotel_nome,
                dl.cidade,
                dl.pais,
                fh.avaliacao,
                fh.preco,
                ROW_NUMBER() OVER (PARTITION BY dl.cidade ORDER BY fh.avaliacao DESC, fh.preco ASC) as ranking
            FROM fato_hospedagem fh
            JOIN dim_localizacao dl ON fh.sk_local = dl.sk_local
            JOIN dim_hotel dh ON fh.sk_hotel = dh.sk_hotel
            WHERE fh.avaliacao > 0
        )
        SELECT 
            hotel_nome,
            cidade,
            pais,
            avaliacao,
            preco,
            ranking
        FROM ranked_hotels
        WHERE ranking <= %s
        ORDER BY cidade, ranking
        """
        
        df = pd.read_sql(query, self.connection, params=[top_n])
        return df
    
    def create_price_comparison_chart(self, df):
        """Criar gráfico de comparação de preços por cidade"""
        plt.figure(figsize=(14, 8))
        
        # Debug: mostrar dados recebidos
        logger.info(f"Dados recebidos para gráfico: {len(df)} linhas")
        logger.info(f"Colunas: {df.columns.tolist()}")
        logger.info(f"Primeiras linhas:\n{df.head()}")
        
        # Criar nome da cidade com país
        df['cidade_completa'] = df['cidade'] + ' (' + df['pais'] + ')'
        
        # Ordenar por preço médio (decrescente)
        df_sorted = df.sort_values('preco_medio', ascending=False)
        
        # Gráfico de barras
        bars = plt.bar(range(len(df_sorted)), df_sorted['preco_medio'], 
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        
        # Customizar gráfico
        plt.title('Comparação de Preços Médios por Cidade', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Cidades', fontsize=12)
        plt.ylabel('Preço Médio (USD)', fontsize=12)
        plt.xticks(range(len(df_sorted)), df_sorted['cidade_completa'], rotation=45, ha='right')
        
        # Adicionar valores nas barras
        for i, (bar, preco) in enumerate(zip(bars, df_sorted['preco_medio'])):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${preco:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Adicionar informações adicionais
        for i, row in df_sorted.iterrows():
            plt.text(i, row['preco_medio']/2, 
                    f'{row["total_hoteis"]} hotéis\nAvaliação: {row["avaliacao_media"]:.1f}',
                    ha='center', va='center', fontsize=9, color='white', fontweight='bold')
        
        plt.tight_layout()
        return plt
    
    def create_price_distribution_chart(self, df):
        """Criar gráfico de distribuição de preços"""
        plt.figure(figsize=(12, 6))
        
        # Histograma de preços
        plt.hist(df['preco'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(df['preco'].mean(), color='red', linestyle='--', 
                   label=f'Média: ${df["preco"].mean():.0f}')
        plt.axvline(df['preco'].median(), color='green', linestyle='--', 
                   label=f'Mediana: ${df["preco"].median():.0f}')
        
        plt.title('Distribuição de Preços das Hospedagens', fontsize=14, fontweight='bold')
        plt.xlabel('Preço (USD)', fontsize=12)
        plt.ylabel('Frequência', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return plt
    
    def create_rating_analysis_chart(self, df):
        """Criar gráfico de análise por avaliação"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Gráfico 1: Quantidade de hotéis por faixa de avaliação
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        bars1 = ax1.bar(df['faixa_avaliacao'], df['quantidade_hoteis'], color=colors)
        ax1.set_title('Quantidade de Hotéis por Faixa de Avaliação', fontweight='bold')
        ax1.set_ylabel('Quantidade de Hotéis')
        ax1.tick_params(axis='x', rotation=45)
        
        # Adicionar valores nas barras
        for bar, qtd in zip(bars1, df['quantidade_hoteis']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(qtd), ha='center', va='bottom', fontweight='bold')
        
        # Gráfico 2: Preço médio por faixa de avaliação
        bars2 = ax2.bar(df['faixa_avaliacao'], df['preco_medio'], color=colors)
        ax2.set_title('Preço Médio por Faixa de Avaliação', fontweight='bold')
        ax2.set_ylabel('Preço Médio (USD)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Adicionar valores nas barras
        for bar, preco in zip(bars2, df['preco_medio']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${preco:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return plt
    
    def create_city_rating_scatter(self, df):
        """Criar gráfico de dispersão: preço vs avaliação por cidade"""
        plt.figure(figsize=(12, 8))
        
        # Cores diferentes para cada cidade
        cities = df['cidade'].unique()
        colors = plt.cm.Set3(range(len(cities)))
        
        for i, city in enumerate(cities):
            city_data = df[df['cidade'] == city]
            # Adicionar país na legenda se disponível
            country = city_data['pais'].iloc[0] if 'pais' in city_data.columns else ''
            label = f"{city} ({country})" if country else city
            
            plt.scatter(city_data['avaliacao'], city_data['preco'], 
                       label=label, color=colors[i], alpha=0.7, s=60)
        
        plt.title('Relação entre Preço e Avaliação por Cidade', fontsize=14, fontweight='bold')
        plt.xlabel('Avaliação', fontsize=12)
        plt.ylabel('Preço (USD)', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return plt
    
    def create_rating_volume_chart(self, df):
        """Criar gráfico de relação entre número de hotéis e nota média por cidade"""
        plt.figure(figsize=(14, 8))
        
        # Agrupar por cidade e calcular estatísticas
        city_stats = df.groupby(['cidade', 'pais']).agg({
            'avaliacao': ['mean', 'count', 'std'],
            'preco': 'mean'
        }).round(2)
        
        # Flatten column names
        city_stats.columns = ['avaliacao_media', 'total_hoteis', 'avaliacao_std', 'preco_medio']
        city_stats = city_stats.reset_index()
        
        # Criar nome da cidade com país
        city_stats['cidade_completa'] = city_stats['cidade'] + ' (' + city_stats['pais'] + ')'
        
        # Gráfico de dispersão
        scatter = plt.scatter(city_stats['total_hoteis'], city_stats['avaliacao_media'], 
                             s=city_stats['preco_medio']*2,  # Tamanho baseado no preço
                             alpha=0.7, c=range(len(city_stats)), cmap='viridis')
        
        # Adicionar labels para cada cidade
        for i, row in city_stats.iterrows():
            plt.annotate(row['cidade_completa'], 
                        (row['total_hoteis'], row['avaliacao_media']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9, fontweight='bold')
        
        # Adicionar linha de tendência
        z = np.polyfit(city_stats['total_hoteis'], city_stats['avaliacao_media'], 1)
        p = np.poly1d(z)
        plt.plot(city_stats['total_hoteis'], p(city_stats['total_hoteis']), 
                "r--", alpha=0.8, linewidth=2, label=f'Tendência (coef: {z[0]:.3f})')
        
        plt.title('Relação entre Número de Hotéis e Nota Média por Cidade', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Número de Hotéis na Cidade', fontsize=12)
        plt.ylabel('Nota Média de Avaliação', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Adicionar informações adicionais
        plt.text(0.02, 0.98, f'Tamanho da bolha = Preço médio\nTotal de cidades: {len(city_stats)}', 
                transform=plt.gca().transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        return plt
    
    def create_top_hotels_chart(self, df):
        """Criar gráfico das melhores hospedagens por cidade"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        axes = axes.flatten()
        
        cities = df['cidade'].unique()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, city in enumerate(cities):
            if i >= len(axes):
                break
                
            city_data = df[df['cidade'] == city].head(5)  # Top 5 por cidade
            
            # Gráfico de barras horizontais
            y_pos = np.arange(len(city_data))
            bars = axes[i].barh(y_pos, city_data['avaliacao'], 
                               color=colors[i % len(colors)], alpha=0.8)
            
            # Customizar eixo Y com nomes dos hotéis (truncados)
            hotel_names = [name[:30] + '...' if len(name) > 30 else name 
                          for name in city_data['hotel_nome']]
            axes[i].set_yticks(y_pos)
            axes[i].set_yticklabels(hotel_names, fontsize=8)
            
            # Adicionar valores nas barras
            for j, (bar, rating, price) in enumerate(zip(bars, city_data['avaliacao'], city_data['preco'])):
                axes[i].text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                           f'{rating:.1f}⭐\n${price:.0f}', 
                           va='center', ha='left', fontsize=8, fontweight='bold')
            
            # Configurar gráfico
            country = city_data['pais'].iloc[0] if len(city_data) > 0 else ''
            axes[i].set_title(f'Top 5 - {city} ({country})', fontsize=12, fontweight='bold')
            axes[i].set_xlabel('Avaliação', fontsize=10)
            axes[i].set_xlim(0, 10)
            axes[i].grid(True, alpha=0.3, axis='x')
        
        # Remover subplots vazios
        for i in range(len(cities), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Melhores Hospedagens por Cidade', fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        return plt
    
    def create_hotel_ranking_table(self, df):
        """Criar tabela de ranking dos melhores hotéis"""
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.axis('tight')
        ax.axis('off')
        
        # Preparar dados para tabela
        table_data = []
        for city in df['cidade'].unique():
            city_data = df[df['cidade'] == city].head(3)  # Top 3 por cidade
            for _, row in city_data.iterrows():
                table_data.append([
                    f"{row['cidade']} ({row['pais']})",
                    row['hotel_nome'][:40] + '...' if len(row['hotel_nome']) > 40 else row['hotel_nome'],
                    f"{row['avaliacao']:.1f}⭐",
                    f"${row['preco']:.0f}",
                    f"#{row['ranking']}"
                ])
        
        # Criar tabela
        table = ax.table(cellText=table_data,
                        colLabels=['Cidade', 'Hotel', 'Avaliação', 'Preço', 'Ranking'],
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        # Estilizar tabela
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Colorir cabeçalho
        for i in range(5):
            table[(0, i)].set_facecolor('#4ECDC4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Colorir linhas alternadas
        for i in range(1, len(table_data) + 1):
            for j in range(5):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f0f0f0')
        
        plt.title('Ranking das Melhores Hospedagens por Cidade', 
                 fontsize=16, fontweight='bold', pad=20)
        
        return plt
    
    def generate_dashboard(self):
        """Gerar dashboard completo"""
        logger.info("Iniciando geração do dashboard...")
        
        # Criar pasta de saída
        output_dir = "outputs/dashboards"
        os.makedirs(output_dir, exist_ok=True)
        
        # Consultar dados
        price_by_city = self.get_price_by_city()
        hotels_by_rating = self.get_hotels_by_rating()
        price_distribution = self.get_price_distribution()
        rating_analysis = self.get_rating_analysis()
        top_hotels = self.get_top_hotels_by_city(5)
        
        # Gerar gráficos
        logger.info("Gerando gráfico de comparação de preços por cidade...")
        chart1 = self.create_price_comparison_chart(price_by_city)
        chart1.savefig(f"{output_dir}/preco_por_cidade.png", dpi=300, bbox_inches='tight')
        chart1.show()
        
        logger.info("Gerando gráfico de distribuição de preços...")
        chart2 = self.create_price_distribution_chart(price_distribution)
        chart2.savefig(f"{output_dir}/distribuicao_precos.png", dpi=300, bbox_inches='tight')
        chart2.show()
        
        logger.info("Gerando gráfico de análise por avaliação...")
        chart3 = self.create_rating_analysis_chart(hotels_by_rating)
        chart3.savefig(f"{output_dir}/analise_avaliacao.png", dpi=300, bbox_inches='tight')
        chart3.show()
        
        logger.info("Gerando gráfico de dispersão preço vs avaliação...")
        chart4 = self.create_city_rating_scatter(price_distribution)
        chart4.savefig(f"{output_dir}/preco_vs_avaliacao.png", dpi=300, bbox_inches='tight')
        chart4.show()
        
        logger.info("Gerando gráfico de relação número de hotéis vs nota média...")
        chart5 = self.create_rating_volume_chart(rating_analysis)
        chart5.savefig(f"{output_dir}/volume_vs_avaliacao.png", dpi=300, bbox_inches='tight')
        chart5.show()
        
        logger.info("Gerando gráfico das melhores hospedagens por cidade...")
        chart6 = self.create_top_hotels_chart(top_hotels)
        chart6.savefig(f"{output_dir}/melhores_hospedagens.png", dpi=300, bbox_inches='tight')
        chart6.show()
        
        logger.info("Gerando tabela de ranking dos melhores hotéis...")
        chart7 = self.create_hotel_ranking_table(top_hotels)
        chart7.savefig(f"{output_dir}/ranking_hoteis.png", dpi=300, bbox_inches='tight')
        chart7.show()
        
        # Salvar dados em CSV
        price_by_city.to_csv(f"{output_dir}/dados_preco_por_cidade.csv", index=False)
        hotels_by_rating.to_csv(f"{output_dir}/dados_avaliacao.csv", index=False)
        price_distribution.to_csv(f"{output_dir}/dados_completos.csv", index=False)
        rating_analysis.to_csv(f"{output_dir}/dados_analise_avaliacao.csv", index=False)
        top_hotels.to_csv(f"{output_dir}/dados_melhores_hoteis.csv", index=False)
        
        logger.info(f"Dashboard gerado com sucesso em {output_dir}/")
        
        # Mostrar resumo
        print("\n" + "="*60)
        print("📊 RESUMO DO DASHBOARD")
        print("="*60)
        print(f"🏙️  Cidades analisadas: {len(price_by_city)}")
        print(f"🏨  Total de hotéis: {len(price_distribution)}")
        print(f"💰  Preço médio geral: ${price_distribution['preco'].mean():.2f}")
        print(f"⭐  Avaliação média geral: {price_distribution['avaliacao'].mean():.2f}")
        print(f"📈  Cidade mais cara: {price_by_city.iloc[0]['cidade']} ({price_by_city.iloc[0]['pais']}) - ${price_by_city.iloc[0]['preco_medio']:.2f}")
        print(f"📉  Cidade mais barata: {price_by_city.iloc[-1]['cidade']} ({price_by_city.iloc[-1]['pais']}) - ${price_by_city.iloc[-1]['preco_medio']:.2f}")
        print("\n🏙️  Cidades no estudo:")
        for _, row in price_by_city.iterrows():
            print(f"   • {row['cidade']} ({row['pais']}) - {row['total_hoteis']} hotéis - ${row['preco_medio']:.0f} médio")
        print("="*60)
    
    def close(self):
        """Fechar conexão"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    analyzer = DataWarehouseAnalyzer()
    analyzer.connect()
    analyzer.generate_dashboard()
    analyzer.close()
    print("Dashboard gerado com sucesso!")
