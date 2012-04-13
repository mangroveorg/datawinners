1. install tomcat

2. copy "BirtViewerExample" in webapps

3. in "BirtViewerExample" create directory META-INF and copy context.xml into it

4. in BirtViewerExample/WEB-INF/web.xml add following code before "</web-app>"
		<resource-ref>
			<description>Resource reference to a factory for java.sql.Connection</description>
			<res-ref-name>jdbc/postgres</res-ref-name>
			<res-type>javax.sql.DataSource</res-type>
			<res-auth>Container</res-auth>
		</resource-ref>

5. create user "reporting" for psql db. set its password as "password". and as postgres user grant select access to it on all the CRS tables :
grant select on crs_physicalinventorysheet to reporting;grant select on crs_sfmdistribution to reporting;grant select on crs_siteactivities to reporting;grant select on crs_warehouse to reporting;grant select on crs_waybillreceived to reporting;grant select on crs_waybillsent to reporting;

6. copy postgresql jdbc4 jar in WEB-INF/lib. The driver VERSION should match that of PostgreSQL installed on your machine

7. Go into the directory : tomcat_dir/webapps/birt-dir/

and  create a SYMLINK  to datawinners/custom_reports/crs by issuing the command: 'ln -s /proj_dir/datawinnners/custom_reports/crs ./crs'
