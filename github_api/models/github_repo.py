from odoo import _, fields, models
from odoo.exceptions import ValidationError


class GithubRepo(models.Model):
    """Model about github repo and how to communicate with it."""

    _name = 'github.repo'
    _description = "Github Repository"

    name = fields.Char(required=True, help="Name of the repository")
    owner = fields.Char(required=True, help="Github organization or github username")
    auth_id = fields.Many2one(
        'github.auth',
        required=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda s: s.env.company,
    )

    _sql_constraints = [
        (
            'name_owner_company_id_uniq',
            'unique (name, owner, company_id)',
            'The name must be unique !',
        )
    ]

    def get_repo(self, name: str, owner: str, company, raise_not_found=False, **kw):
        repo = self.search(
            self.prepare_repo_domain(name, owner, company, **kw), limit=1
        )
        if not repo and raise_not_found:
            raise ValidationError(
                _("Github Repo Not Found. Make sure it is configured properly!")
            )
        return repo

    def prepare_repo_domain(self, name: str, owner: str, company, **kw):
        """Prepare domain to get github.repo record."""
        return [
            ('name', '=', name),
            ('owner', '=', owner),
            ('company_id', '=', company.id),
        ]
