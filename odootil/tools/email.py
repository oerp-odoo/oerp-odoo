from footil.formatting import email_to_domain


def is_email_in_domains(email, domains):
    return email_to_domain(email) in domains
