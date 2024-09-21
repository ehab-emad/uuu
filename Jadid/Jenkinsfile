#!/usr/bin/env groovy

@Library('jenkinslib@master')_

pipeline {
    environment {
        MAVEN_PROPERTIES = "-Dparam=example"
    }
    agent {
        kubernetes {
          yaml '''
          apiVersion: v1 
          kind: Pod
          spec:
            containers:
            - name: python
              image: python:3.10
              command:
              - cat
              tty: true
            - name: kaniko
              image: gcr.io/kaniko-project/executor:debug
              command: ["/busybox/cat"]
              tty: true                
            - name: clamav
              image: clamav/clamav
              command:
              - cat
              tty: true
            - name: sonarscanner
              image: sonarsource/sonar-scanner-cli
              command:
              - cat
              tty: true		   
          '''
        }
    }
    stages {
    //     stage('Set Certificates') {
    //         steps {
    //             container('python') {
    //                 sh '''
    //                 wget https://crl.edag.de/EDAG%20Engineering%20SUBCA4.crt -O edag-ssl.crt

    //                 '''

    //             }
    //         }
    //     }
    //     stage('Build') {
    //         steps {
    //             container('python') {
	// 			    sh "cat requirements.txt  | grep -v digi | grep -v pywin32 > requirements2.txt"
	// 				sh "pip install --upgrade pip setuptools==57.5.0"
	// 				sh "pip install -r requirements2.txt"
    //             }
    //         }
    //     }

    //     stage('License') {
    //         steps {
    //             container('sonarscanner') {
	// 				sh "pip install -U pip-licenses" 
    //                 sh "pip-licenses"
    //             }
    //         }
    //     }
		
    //     stage('Code Quality') {
    //         steps {
    //             container('sonarscanner') {
    //                 sh "sonar-scanner -Dsonar.host.url='https://x06-sonarqube.edag.de/'"
    //             }
    //         }
    //     }

    //    stage('CVE') {
    //         steps {
    //             container('python') {
    //                 sh "python -m pip install pip-audit"
	// 				sh "pip-audit -r requirements2.txt"
    //             }
    //         }
    //     }
        
        stage('Docker Image') {
            steps {
                container('kaniko') {
                    script {
                        if (env.BRANCH_NAME == 'master') {
                          String version = "build_number_${BUILD_NUMBER}"
                          kaniko.add_certificate_from_url('https://crl.edag.de/EDAG%20Engineering%20SUBCA4.crt')
                          kaniko.set_credentials('fdslphost006.service-hosting.org:9001', 'its-nexus')
                          kaniko.build_and_push(
                                  'Dockerfile',
                                  '.',
                                  "fdslphost006.service-hosting.org:9001/be_paramount:${version}",
                                  version.isEmpty() ? false : true,
                                  true,
                                  true)
                        }
                        if (env.BRANCH_NAME == 'develop') {
                          String version = "develop_build_number_${BUILD_NUMBER}"
                          kaniko.add_certificate_from_url('https://crl.edag.de/EDAG%20Engineering%20SUBCA4.crt')
                          kaniko.set_credentials('fdslphost006.service-hosting.org:9001', 'its-nexus')
                          kaniko.build_and_push(
                                  'Dockerfile',
                                  '.',
                                  "fdslphost006.service-hosting.org:9001/be_paramount:${version}",
                                  version.isEmpty() ? false : true,
                                  true,
                                  true)
                        }
                    }
                }
            }
        }


        // stage('Virus Scan') {
        //     steps {
        //         container('clamav') {
        //             sh '''clamscan -ir . \
        //                 --alert-encrypted-doc=yes \
        //                 --alert-encrypted-archive=yes \
        //                 --alert-encrypted=yes \
        //                 --alert-macros=yes \
        //                 --alert-broken=yes \
        //                 --exclude-dir=src/test \
        //                 --exclude-dir=target/test-classes'''
        //         }
        //     }
        // }
    }
}
