from datawinners.main.database import get_db_manager


nan_submissions = """
function(doc) {
    if (doc.document_type == 'SurveyResponse' && doc.form_model_id == '16ff92ba2d5511e68c6d12313d2da6d0'
      && (doc.values['section_service'][0]['pafp_calc1']== 'NaN'
      || doc.values['section_service'][0]['pafp_calc2']== 'NaN'
      || doc.values['section_client2'][0]['service_totalfp'] == 'NaN')) {
        emit(doc.form_model_id, doc);
    }
}
"""

db_name = "hni_marie-stopes-int-cambodia_ejn610045"

manager = get_db_manager(db_name)


def get_numerator(submission_dict):
    numerators = ['pafp_m_cd', 'pafp_m_pill', 'pafp_m_inj', 'pafp_m_imp', 'pafp_m_iud', 'pafp_s_cd', 'pafp_s_pill', 'pafp_s_inj', 'pafp_s_imp', 'pafp_s_iud']
    total = 0
    for numerator in numerators:
        try:
            total += int(submission_dict['value']['values']['section_service'][0][numerator])
        except Exception as e:
            pass
    return total


def get_denumerator(submission_dict):
    denumerators = ['service_cacm', 'service_cacs']
    total = 0
    for denumerator in denumerators:
        try:
            total += int(submission_dict['value']['values']['section_service'][0][denumerator])
        except Exception as e:
            pass
    return total

def calculate_pafp_calc1(row):
    den = get_denumerator(row)
    if den == 0:
        return 0
    return 100 * get_numerator(row)/ den


def get_total_servicefp(submission_dict):
    services = ['service_counselling', 'service_ec', 'service_male_condom', 'service_pill', 'service_injectable',
    'service_implant', 'service_iud', 'service_tl', 'service_vasectomy', 'service_STI', 'service_cacm', 'service_cacs']
    total = 0
    for sce in services:
        try:
            total += int(submission_dict['value']['values']['section_service'][0][sce])
        except Exception as e:
            pass
    return total
   

i = 0

for row in manager.database.query(nan_submissions):
    try:
        pafp_calc1 = calculate_pafp_calc1(row)
        calc1 = row['value']['values']['section_service'][0]['pafp_calc1']
        pafp_calc2 = int(pafp_calc1)
        total_servicefp = get_total_servicefp(row)
        current_total = row['value']['values']['section_client2'][0]['service_totalfp']
        summ = total_servicefp + pafp_calc1

        row['value']['values']['section_service'][0]['pafp_calc1'] = str(pafp_calc1)
        row['value']['values']['section_service'][0]['pafp_calc2'] = str(pafp_calc2)
        row['value']['values']['section_client2'][0]['service_totalfp'] = str(total_servicefp)
        
        manager.database.save(row['value'], process_post_update=False)
        print "\n%s - %s" % (i, row['id'])
        i += 1
    except KeyError as e:
        print "\n%s - %s KeyError" % (i, row['id'])
        i += 1
        pass
    except Exception as e:
        raise