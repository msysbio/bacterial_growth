import io
import csv


def export_model_csv(db_session, study):
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=[
            'bioreplicate',
            'compartment',
            'subject_type',
            'subject_name',
            'model_type',
            'y0',
            'mumax',
            'lag',
            'y0_lm',
            'K',
            'h0',
            'r2',
            'rss',
        ]
    )
    writer.writeheader()

    for modeling_result in study.modelingResults:
        if modeling_result.state != 'ready':
            continue

        measurement_context = modeling_result.measurementContext
        subject = measurement_context.get_subject(db_session)

        writer.writerow({
            'bioreplicate': measurement_context.bioreplicate.name,
            'compartment':  measurement_context.compartment.name,
            'subject_type': measurement_context.subjectType,
            'subject_name': subject.name,
            'model_type':   modeling_result.model_name,
            # Coefficients:
            'y0':    modeling_result.coefficients.get('y0',    None),
            'mumax': modeling_result.coefficients.get('mumax', None),
            'lag':   modeling_result.coefficients.get('lag',   None),
            'y0_lm': modeling_result.coefficients.get('y0_lm', None),
            'K':     modeling_result.coefficients.get('K',     None),
            'h0':    modeling_result.coefficients.get('h0',    None),
            # Fit:
            'r2':  modeling_result.fit.get('r2',  None),
            'rss': modeling_result.fit.get('rss', None),
        })

    return buf.getvalue().encode('utf-8')
