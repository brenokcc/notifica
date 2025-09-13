import os
import psycopg2
import psycopg2.extras
import datetime


def consulta_cpf(cpf):

    if not os.environ.get('ESUS_POSTGRES_PASSWORD'):
        return {}

    if os.environ.get('ESUS_POSTGRES_PASSWORD') == 'test':
        return MOCKED_DATA

    conn = psycopg2.connect(
    dbname=os.environ.get('ESUS_POSTGRES_DATABASE', 'esus'),
    user=os.environ.get('ESUS_POSTGRES_USER', 'esus_leitura'),
    password=os.environ.get('ESUS_POSTGRES_PASSWORD', 'QdvSO{6K1bDE3_3S-JFy1xEQvBR5zH'),
    host=os.environ.get('ESUS_POSTGRES_HOST', '10.10.10.219'),
    port=os.environ.get('ESUS_POSTGRES_PORT', '5433')
    )

    sql = """
    with 
        stg_cpf_busca as ( 
        select '{cpf}'::text as cpf_busca
        -- select '81545711100'::text as cpf_busca
        --select '04717379179'::text as cpf_busca
        --select '08655467111'::text as cpf_busca
        
        ),
        
        stg_csc_busca_co_cidadao as ( 
    
            select  tc.nu_cpf
                , max(tc.co_seq_cidadao) co_seq_cidadao
                
            from tb_cidadao tc 
            
            where tc.st_ativo = 1 
                and tc.dt_obito is null
                --and tc.nu_cpf is not null
                and tc.nu_cpf = (select cpf_busca from stg_cpf_busca)
            group by tc.nu_cpf 
    
        ),
        
        stg_parametros as ( 
        
            select tc.co_seq_cidadao
                ,tc.co_unico_ultima_ficha
                ,tc.dt_ultima_ficha
                ,pec.co_seq_fat_cidadao_pec
                
            from tb_cidadao tc 
            
            inner join stg_csc_busca_co_cidadao stg 
                    on stg.co_seq_cidadao = tc.co_seq_cidadao
                    
                left join tb_fat_cidadao_pec pec 
                    on pec.co_cidadao = tc.co_seq_cidadao 
        
        ),
        
        stg_csc_dados_individuo as ( 
        
            select --Dados do Individuo
                tc.co_seq_cidadao                 
                ,tc.nu_cpf                        
                ,tc.nu_cns                         
                ,tc.no_cidadao                     
                ,tc.dt_nascimento                 
                ,tc.no_sexo                          
                --,tc.co_raca_cor
                ,tdrc.ds_raca_cor                    
                -- ,tc.co_escolaridade
                ,tdte.ds_dim_tipo_escolaridade    
                ,tc.no_mae                        
                
                --Dados Residenciais
                --DESCONSIDERAR, ''--,tc.pais
                
                --,tc.co_localidade_endereco
                
                --distrito
                -- DESCONSIDERAR--zona
                ,null::text tp_logradouro                
                ,tc.ds_logradouro                                  --DESCONSIDERAR ,tc.ds_cep --co_logradouro
                ,tc.nu_numero                        
                ,tc.ds_complemento                
                ,tc.no_bairro                        
                ,tc.ds_cep                        
                ,tl.no_localidade                    
                
                
                --Dados para Contato
                ,tc.nu_telefone_celular            
                ,tc.ds_email                        
                --atualizado_ultimos_doze_meses=True
                
                
                ,case when tc.co_unico_ultima_ficha is not null 
                            then true 
                            else false 
                    end reg_fci
                ,tc.co_unico_ultima_ficha        
                ,tc.dt_ultima_ficha              
                ,case when tc.co_unico_ultima_ficha is not null 
                            then 
                                case when extract(year from age(current_date, tc.dt_ultima_ficha)) > 0 
                                            then false
                                            else true
                                end 
                                                                        
                            else  null
                    end FCI_Atualizada                 
                    
                    
                    ,tc.dt_atualizado                 
                    ,tc.st_registro_cadsus             
                    ,tc.dt_atualizado_cadsus        
                    
                    
                    
                    ,pec.co_seq_fat_cidadao_pec     
                
            from tb_cidadao tc 
            
            left join tb_dim_raca_cor tdrc  
                    on tdrc.co_seq_dim_raca_cor = tc.co_raca_cor
                    
            left join tb_dim_tipo_escolaridade tdte 
                    on tdte.co_seq_dim_tipo_escolaridade  = tc.co_escolaridade 
                    
            left join tb_fat_cidadao_pec pec  
                    on pec.co_cidadao = tc.co_seq_cidadao 
                    
            left join tb_localidade tl  
                    on tl.co_localidade = tc.co_localidade_endereco
                
            
                    
            where tc.co_seq_cidadao = (select co_seq_cidadao from stg_parametros)
            
            --inner join stg_csc_id_ativo ida 
            --        on ida.co_seq_cidadao = tc.co_seq_cidadao 
        
        
        ),
        
        stg_fci_dados_individuo as ( 
        
    -------------------------------------------------------------------------------------
    -- FICHA DE CADASTRO INDIVIDUAL 
    ------------------------------------------------------------------------------------

            select tfci.co_seq_fat_cad_individual
                ,tfci.nu_cpf_cidadao
                ,tfci.nu_cns
                ,tcci.no_cidadao
                ,tfci.dt_nascimento
                --,tfci.co_dim_sexo
                ,tds.ds_sexo
                --,tfci.co_dim_raca_cor
                ,tdrc.ds_raca_cor
                --,tfci.co_dim_tipo_escolaridade
                ,tdte.ds_dim_tipo_escolaridade
                ,tcci.no_mae_cidadao
                ,tcci.nu_celular_cidadao
                ,tcci.ds_email_cidadao
                ,tfci.co_dim_tempo
                ,tfci.nu_uuid_ficha 
            
                ---,'||||||||||||||||||||||' tfci
                --,tfci.*
                --,'||||||||||||||||||||||' tcci
                --,tcci.*
                
            from tb_fat_cad_individual tfci 
            
            left join tb_cds_cad_individual tcci 
                    on tcci.co_unico_ficha  = tfci.nu_uuid_ficha
                    
            left join tb_dim_sexo tds 
                    on tds.co_seq_dim_sexo  = tfci.co_dim_sexo
                    
            left join tb_dim_raca_cor tdrc  
                    on tdrc.co_seq_dim_raca_cor = tfci.co_dim_raca_cor
                    
            left join tb_dim_tipo_escolaridade tdte 
                    on tdte.co_seq_dim_tipo_escolaridade  = tfci.co_dim_tipo_escolaridade 
            
            --where nu_uuid_ficha = '2710870-8b414969-6961-4ce7-888b-38c9ed50801f';
            where nu_uuid_ficha = (select co_unico_ultima_ficha from stg_parametros)    
        
        ), 
        
        stg_fcd_dados_domicilio as ( 
        
            -------------------------------------------------------------------------------------
            -- FICHA DE CADASTRO DOMICILIAR 
            ------------------------------------------------------------------------------------                                                                    
            
            select 
                    tccd.co_seq_cds_cad_domiciliar
                    
                    --,tccd.tp_logradouro
                    ,tdtl.ds_tipo_logradouro
                    ,tccd.no_logradouro
                    ,tccd.nu_domicilio
                    ,tccd.ds_complemento
                    ,tccd.no_bairro
                    ,tccd.nu_cep
                    --,tccd.co_municipio
                    ,tdm.no_municipio
            
                    -- Dados de Contato
                    ,tccd.nu_fone_referencia
                    --,tccd.* 
                    --, '||||||||||||' tfcd
                    --, tfcd.*
                    ,tfcpgf.co_seq_fat_cidadao_pec 
                    ,tccd.nu_latitude
                    ,tccd.nu_longitude
                
            from tb_cds_cad_domiciliar  tccd 
            
            --CDS - Cadastro domiciliar ( INFO de descritivo do endereço)
            inner join tb_fat_cad_domiciliar tfcd 
                    on tccd.co_unico_ficha = tfcd.nu_uuid_ficha
                    
            --Responsavel Familiar
            inner join tb_fat_cad_dom_familia tfcdf 
                    on tfcdf.co_fat_cad_domiciliar = tfcd.co_seq_fat_cad_domiciliar
                    
                
            --TAB REF:Grupo Familiar - Tabela com codigo de referencia para o grupo familiar
            inner join tb_fat_familia_territorio tfft 
                    on tfft.co_fat_cad_domiciliar     = tfcdf.co_fat_cad_domiciliar 
            
                    
            inner join tb_fat_cidadao_territorio tfct  
                    on tfct.co_seq_fat_cidadao_territorio = tfft.co_fat_cidadao_territorio
                    --on tfct.co_fat_cad_domiciliar = tfft.co_seq_fat_cad_domiciliar 
                    
                --Cidadao PEC: para x grupo familiar      
            inner join tb_fat_cidadao_pec tfcpgf 
                    on tfcpgf.co_seq_fat_cidadao_pec = tfct.co_fat_cidadao_pec    
            
                left join tb_dim_municipio tdm
                    on tdm.co_seq_dim_municipio = tccd.co_municipio
                    
                left join tb_dim_tipo_logradouro tdtl 
                    on tdtl.co_seq_dim_tipo_logradouro = tccd.tp_logradouro 
            
            -- where tccd.co_seq_fat_cidadao = '2710870-5868c71f-e542-44dc-8202-431074e1fc99'
            
            --where tccd.co_unico_ficha = '2710870-5868c71f-e542-44dc-8202-431074e1fc99' 
            where tfcpgf.co_seq_fat_cidadao_pec = (select co_seq_fat_cidadao_pec from stg_parametros )
        
        
        ),
        
        stg_uniao_tab as (  
        
            select  '||||||||||||||||||||||' as cadastro_simplificado
                
                
                ,tc.nu_cpf                        as csc_cpf 
                ,tc.nu_cns                        as csc_cns
                ,tc.no_cidadao                    as csc_cidadao
                ,tc.dt_nascimento                as csc_dt_nascimento 
                ,tc.no_sexo                        as csc_sexo 
                ,tc.ds_raca_cor                    as csc_raca_cor 
                ,tc.ds_dim_tipo_escolaridade        as csc_escolaridade
                ,tc.no_mae                        as csc_mae 
                ,tc.tp_logradouro                as csc_tipo_logradouro 
                ,tc.ds_logradouro                as csc_logradouro 
                ,tc.nu_numero                    as csc_numero 
                ,tc.ds_complemento                as csc_complemento 
                ,tc.no_bairro                    as csc_bairro 
                ,tc.ds_cep                        as csc_cep 
                ,tc.no_localidade                as csc_localidade 
                ,tc.nu_telefone_celular            as csc_celular 
                ,tc.ds_email                        as csc_email 
                ,tc.reg_fci                        as csc_reg_fci 
                ,tc.co_unico_ultima_ficha        as csc_co_unico_ultima_ficha 
                ,tc.dt_ultima_ficha                as csc_dt_ultima_ficha 
                ,tc.fci_atualizada                as csc_fci_atualizada
                ,tc.dt_atualizado                as csc_dt_registro
                ,tc.st_registro_cadsus            as csc_registro_cadsus 
                ,tc.dt_atualizado_cadsus            as csc_dt_atualizado_cadsus 
                ,tc.co_seq_fat_cidadao_pec        as csc_co_seq_fat_cidadao_pec
                ,tc.co_seq_cidadao                as csc_co_seq_cidadao
                
                ,'||||||||||||||||||||||' as ficha_fci 
                ,fci.nu_cpf_cidadao                as fci_cpf
                ,fci.nu_cns                        as fci_cns
                ,fci.no_cidadao                    as fci_cidadao
                ,fci.dt_nascimento                as fci_dt_nascimento
                ,fci.ds_sexo                        as fci_sexo
                ,fci.ds_raca_cor                    as fci_raca_cor
                ,fci.ds_dim_tipo_escolaridade    as fci_escolaridade
                ,fci.no_mae_cidadao                as fci_mae
                ,fci.nu_celular_cidadao            as fci_celular
                ,fci.ds_email_cidadao            as fci_email
                ,fci.co_dim_tempo                as fci_dt_registro
                ,fci.nu_uuid_ficha                as fci_nu_uuid_ficha
                ,fci.co_seq_fat_cad_individual    as fci_co_seq_fat_cad_individual
                
                ,'||||||||||||||||||||||' as ficha_fcd
                ,fcd.ds_tipo_logradouro            as fcd_tipo_logradouro
                ,fcd.no_logradouro                as fcd_logradouro
                ,fcd.nu_domicilio                as fcd_numero
                ,fcd.ds_complemento                as fcd_complemento
                ,fcd.no_bairro                    as fcd_bairro
                ,fcd.nu_cep                        as fcd_cep
                ,fcd.no_municipio                as fcd_municipio
                ,fcd.co_seq_fat_cidadao_pec        as fcd_co_seq_fat_cidadao_pec
                ,fcd.co_seq_cds_cad_domiciliar    as fcd_co_seq_cds_cad_domiciliar
                ,fcd.nu_latitude                    as fcd_latitude
                ,fcd.nu_longitude                as fcd_longitude
                
            
                
            from stg_csc_dados_individuo tc
            
            left join stg_fci_dados_individuo fci  
                    on fci.nu_uuid_ficha = tc.co_unico_ultima_ficha
            
            left join stg_fcd_dados_domicilio fcd 
                    on fcd.co_seq_fat_cidadao_pec = tc.co_seq_fat_cidadao_pec 
    
    
    ),
        --select * from stg_uniao_tab       
    tb_dados_cidadao as ( 
    
            select coalesce(fci_cpf, csc_cpf) as cpf 
                    ,coalesce(fci_cns, csc_cns) as cns
                    ,coalesce(fci_cidadao, csc_cidadao) as cidadao 
                    ,coalesce(fci_dt_nascimento, csc_dt_nascimento) as dt_nascimento 
                    ,coalesce(fci_sexo, csc_sexo) as sexo 
                    ,coalesce(fci_raca_cor, csc_raca_cor) as raca_cor 
                    ,coalesce(fci_escolaridade, csc_escolaridade) as escolaridade 
                    ,coalesce(fci_mae, csc_mae) as mae 
                    ,coalesce(fci_celular, csc_celular) as celular 
                    ,coalesce(fci_email, csc_email) as email 
                    
                    ,coalesce(fcd_tipo_logradouro, csc_tipo_logradouro) as tipo_logradouro  
                    ,coalesce(fcd_logradouro, csc_logradouro) as logradouro  
                    ,coalesce(fcd_numero, csc_numero) as numero  
                    ,coalesce(fcd_complemento, csc_complemento) as complemento 
                    ,coalesce(fcd_bairro, csc_bairro) as bairro 
                    ,coalesce(fcd_cep, csc_cep) as cep 
                    ,coalesce(fcd_municipio, csc_localidade) as municipio 
                    ,coalesce(fcd_latitude, null) as latitude
                    ,coalesce(fcd_longitude, null) as longitude

                    ,csc_reg_fci  as registro_fci
                    ,csc_fci_atualizada as fci_atualizada
                    ,csc_registro_cadsus as registro_cadsus
                    ,csc_dt_atualizado_cadsus as dt_atualizado_cadsus
                    
                    ,csc_co_seq_cidadao as id_cidadao
                    ,csc_co_seq_fat_cidadao_pec as id_cidadao_pec
                    ,csc_co_unico_ultima_ficha as id_fci_ultima_ficha
                    ,csc_dt_ultima_ficha as dt_ultima_ficha
                    ,fci_co_seq_fat_cad_individual as id_fci
                    ,fcd_co_seq_cds_cad_domiciliar as id_fcd_cds
                    
                    
                    
                from stg_uniao_tab
    
    )
    
    select * from tb_dados_cidadao
    """.format(cpf=cpf.replace('.', '').replace('-', ''))


    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    print('ESUS', cpf, row)
    return row or {}


MOCKED_DATA = {
    "cpf": "81545711100",
    "cns": "0              ",
    "cidadao": "FABRICIO DA SILVA",
    "dt_nascimento": datetime.date(1977, 5, 26),
    "sexo": "Masculino",
    "raca_cor": "Branca",
    "escolaridade": "Superior, aperfeiçoamento, especialização, mestrado, doutorado",
    "mae": "ANGELA APARECIDA DE LOLLO SILVA",
    "celular": "19996917532",
    "email": "fa_bricio@msn.com",
    "tipo_logradouro": "1ª RUA",
    "logradouro": "RIO BRILHANTE",
    "numero": "285",
    "complemento": "ACS ELIANE",
    "bairro": "JARDIM SÃO PEDRO",
    "cep": "79810070",
    "municipio": "DOURADOS",
    "latitude": -22.2344696,
    "longitude": -54.805347,
    "registro_fci": True,
    "fci_atualizada": True,
    "registro_cadsus": 1,
    "dt_atualizado_cadsus": datetime.date(2020, 7, 13),
    "id_cidadao": 295168,
    "id_cidadao_pec": 1753595,
    "id_fci_ultima_ficha": "2710870-8b414969-6961-4ce7-888b-38c9ed50801f",
    "dt_ultima_ficha": datetime.date(2025, 1, 24),
    "id_fci": 4208805,
    "id_fcd_cds": 877040,
}