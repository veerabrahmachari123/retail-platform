pipeline {
    agent any
    
    parameters {
        choice(name: 'DEPLOYMENT_ACTION', choices: ['DEPLOY', 'ROLLBACK'], description: 'Choose the action to perform.')
        choice(name: 'ENVIRONMENT', choices: ['UAT', 'PRODUCTION'], description: 'Target deployment environment.')
        string(name: 'VERSION', defaultValue: 'main', description: 'Enter the Git branch or tag name to validate.')
        choice(name: 'CONFIRM_PROD', choices: ['NO', 'YES'], description: 'Explicit approval required for PRODUCTION deployments.')
    }

    environment {
        IMAGE_NAME = 'retail-platform'
        CONTAINER_NAME = "retail_app_${params.ENVIRONMENT.toLowerCase()}"
        // Fixed Windows ports cleanly
        APP_PORT = "${params.ENVIRONMENT == 'PRODUCTION' ? '8000' : '8001'}"
        OLD_VERSION = 'Unknown'
        NEW_VERSION = "${params.VERSION}"
        FINAL_STATE = 'NOT STARTED'
    }

    stages {
        stage('Guardrails & Validation') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'PRODUCTION' && params.DEPLOYMENT_ACTION == 'DEPLOY' && params.CONFIRM_PROD != 'YES') {
                        error "Deployment ABORTED: Production deployment requested but CONFIRM_PROD was not set to YES."
                    }
                    
                    echo "Validating workspace code state..."
                    def commitHash = bat(script: "@git rev-parse HEAD", returnStdout: true).trim()
                    echo "Successfully validated target code commit hash: ${commitHash}"
                }
            }
        }

        stage('Build Docker Image') {
            when { expression { params.DEPLOYMENT_ACTION == 'DEPLOY' } }
            steps {
                bat "docker build -t ${IMAGE_NAME}:${params.VERSION} ."
            }
        }

        stage('Record Audit State') {
            steps {
                script {
                    def inspectCmd = "@docker inspect --format=\"{{.Config.Image}}\" ${env.CONTAINER_NAME}"
                    try {
                        def output = bat(script: inspectCmd, returnStdout: true).trim()
                        env.OLD_VERSION = output.tokenize(':')[-1]
                        echo "Audited Architecture: Current active version running is ${env.OLD_VERSION}"
                    } catch (Exception e) {
                        echo "No previous active container instance found. Defaulting old version to none."
                        env.OLD_VERSION = "None (Fresh Setup)"
                    }
                }
            }
        }

        stage('Execute Deployment Flow') {
            when { expression { params.DEPLOYMENT_ACTION == 'DEPLOY' } }
            steps {
                script {
                    env.FINAL_STATE = 'DEPLOYING_NEW_VERSION'
                    def tempContainer = "${env.CONTAINER_NAME}_new"
                    
                    bat "docker rm -f ${tempContainer} 2>nul || exit 0"
                    bat "docker run -d --name ${tempContainer} -p ${env.APP_PORT}:8000 ${IMAGE_NAME}:${params.VERSION}"
                    
                    def healthCheckPassed = false
                    
                    // Windows Native Health Loop (fixed variable substitution)
                    for (int i = 0; i < 6; i++) {
                        sleep 5
                        echo "Performing health probe attempt ${i+1}/6..."
                        
                        // Using explicit parameter mapping for Windows command line parsing
                        def statusCode = bat(script: "@curl -s -o NUL -w \"%%{http_code}\" http://localhost:${env.APP_PORT}/health", returnStdout: true).trim()
                        
                        if (statusCode == "200") {
                            healthCheckPassed = true
                            break
                        }
                        echo "Health check status caught: (${statusCode}). Retrying..."
                    }
                    
                    if (!healthCheckPassed) {
                        env.FINAL_STATE = 'HEALTH_CHECK_FAILED_TRIGGERING_ROLLBACK'
                        bat "docker stop ${tempContainer} && docker rm ${tempContainer}"
                        error "Deployment failed health validation. Automated rollback requested."
                    } else {
                        bat "docker stop ${env.CONTAINER_NAME} 2>nul || exit 0"
                        bat "docker rm ${env.CONTAINER_NAME} 2>nul || exit 0"
                        bat "docker rename ${tempContainer} ${env.CONTAINER_NAME}"
                        env.FINAL_STATE = 'DEPLOYMENT_SUCCESSFUL'
                    }
                }
            }
        }

        stage('Manual Rollback Engine') {
            when { expression { params.DEPLOYMENT_ACTION == 'ROLLBACK' } }
            steps {
                script {
                    env.FINAL_STATE = 'MANUAL_ROLLBACK_EXECUTING'
                    if (env.OLD_VERSION == "None (Fresh Setup)") { error "Rollback aborted: No history found." }
                    bat "docker stop ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker rm ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker run -d --name ${env.CONTAINER_NAME} -p ${env.APP_PORT}:8000 ${IMAGE_NAME}:${env.OLD_VERSION}"
                    env.FINAL_STATE = 'MANUAL_ROLLBACK_COMPLETE'
                }
            }
        }
    }

    post {
        always {
            script {
                echo """
                =======================================================
                📋 PIPELINE EXECUTION SUMMARY
                =======================================================
                ENVIRONMENT:   ${params.ENVIRONMENT}
                ACTION TAKEN:  ${params.DEPLOYMENT_ACTION}
                OLD VERSION:   ${env.OLD_VERSION}
                NEW VERSION:   ${env.NEW_VERSION}
                FINAL STATE:   ${env.FINAL_STATE}
                =======================================================
                """
            }
        }
        failure {
            script {
                if (env.FINAL_STATE == 'HEALTH_CHECK_FAILED_TRIGGERING_ROLLBACK') {
                    currentBuild.result = 'FAILURE'
                }
            }
        }
    }
}
