from continuum_deployer.dsl.importer.importer import Importer


class Terraform(Importer):

    def activate(self):
        print('Demo Plugin activated!')
