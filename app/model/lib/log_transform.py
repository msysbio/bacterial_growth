import numpy as np


def apply_log_transform(df):
    if 'std' in df and not df['std'].isnull().all():
        # Transform std values by summing them and transforming the results:
        with np.errstate(divide='ignore'):
            upper_log = np.log(df['value'] + df['std'])
            lower_log = np.log(df['value'] - df['std'])
            df['std'] = (upper_log - lower_log) / 2.0

    with np.errstate(divide='ignore'):
        df['value'] = np.log(df['value'])
