# tomcat9_rh7
Installs Tomcat 9.0.24 on RHEL7 
#Tomcat 9.0.24 on RHEL6

#Retrieve the RPM to /tmp.

cd /tmp

f3d62b68909061d14cbce66da044720930b3e84b97f9c1a74913d03ad69f9375 tomcat-9.0.24-1.el6.noarch.rpm

yum install --nogpgcheck -y tomcat-9.0.24-1.el6.noarch.rpm

cd /apps/tomcat/webapps

wget http://tomcat.apache.org/tomcat-9.0-doc/appdev/sample/sample.war && chown tomcat.tomcat sample.war

service tomcat start

#Test sample app on a web browser with URL eg: http://URL:8080/sample/

#Expected results:

#The web page should display Sample “Hello, World Application” on Port 8080 of the URL. You can check by clicking on the JSP and Servlet
link to make sure those links work and display JSP and Servlet pages.
