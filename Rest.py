import cherrypy
import sqlite3
import json
import os, os.path

DB_STRING = "project_monitor"

class ProjectManage(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')

class Team:
	exposed = True

	def GET(self):
		with sqlite3.connect(DB_STRING) as con:
			r = con.execute('SELECT distinct lead from project_monitor')
		res = r.fetchall()

		return json.dumps(res)

class Projects:

	exposed = True

	@cherrypy.tools.accept(media='text/plain')
	def GET(self, id=None):
		with sqlite3.connect(DB_STRING) as con:
			con.row_factory = sqlite3.Row
			if id == None:
				r = con.execute('SELECT * from project_monitor where active=1 order by mile_stone')
			else:
				r = con.execute('SELECT * FROM project_monitor WHERE project_id=?', [id])
		res = r.fetchall()

		return json.dumps( [dict(ix) for ix in res] )

	def POST(self, project_id=None, project_name=None, mile_stone=None, lead=None, active=True):
	    with sqlite3.connect(DB_STRING) as con:
	        con.execute('INSERT into project_monitor values(?,?,?,?,?)', [project_id,project_name, mile_stone, lead, active])
	    return "success"

	def DELETE(self, project_id=None):
		print 'calling delete'
		print 'project id', project_id
		with sqlite3.connect(DB_STRING) as con:
			con.execute('UPDATE project_monitor set active=0 where project_id=?', [project_id])

def setup_database():
        with sqlite3.connect(DB_STRING) as c:
                c.execute('CREATE TABLE IF NOT EXISTS project_monitor(project_id, project_name, mile_stone, lead, active)')

if __name__ == '__main__':
	cherrypy.tree.mount(
		Projects(), '/projects',
		{'/':
			{ 'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			  'tools.response_headers.on': True,
              'tools.response_headers.headers': [('Content-Type', 'text/plain')] }
		}
	)
	cherrypy.tree.mount(
		Team(), '/team',
		{'/':
			{ 'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			  'tools.response_headers.on': True,
              'tools.response_headers.headers': [('Content-Type', 'text/plain')] }
		}
	)
	cherrypy.tree.mount(
    		ProjectManage(), '/',
    		{'/':
    		    { 'tools.staticdir.root': os.path.abspath(os.getcwd()) },
             '/static': {
                     'tools.staticdir.on': True,
					 'tools.staticdir.dir': './public'
                     }
             }
    	)
    	cherrypy.engine.subscribe('start', setup_database)
	cherrypy.engine.start()
	cherrypy.engine.block()

