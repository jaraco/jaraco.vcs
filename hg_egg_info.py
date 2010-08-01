from setuptools.command.egg_info import egg_info
from distutils.version import StrictVersion
import hgtools

class EggInfo(egg_info):
	"""
	Override egg_info so that if the current repository revision is
	tagged with a valid StrictVersion, that version will be used, and
	tags will be suppressed.
	"""
	def tags(self):
		if True or self.tag_build.startswith('hgtools'):
			try:
				mgr = hgtools.get_manager()
				if mgr.get_tagged_version():
					# current tag is valid - no tags
					return ''
				else:
					self.tag_build = 'dev'
			except Exception:
				self.tag_build = None
		return egg_info.tags(self)