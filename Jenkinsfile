pipeline {
    agent any

    parameters {
        string(name: 'STUDENT_NAME', defaultValue: 'Иванов Иван', description: 'ФИО студента')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'Среда')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Запускать тесты')
    }

    environment {
        DOCKER_IMAGE = "aroslauh/student-app:${BUILD_NUMBER}"
        CONTAINER_NAME = "student-app-${ENVIRONMENT}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Клонирование репозитория...'
                git branch: 'main',
                    url: 'https://github.com/GolubYaroslav/simple-python-app.git',
                    credentialsId: 'github-credentials'
            }
        }

        stage('Setup Python') {
            steps {
                echo 'Настройка окружения Python...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Tests') {
            when {
                expression { params.RUN_TESTS }
            }
            steps {
                echo 'Запуск тестов...'
                sh '''
                    . venv/bin/activate
                    python -m unittest test_app.py -v
                '''
            }
            post {
                success {
                    echo 'Все тесты пройдены успешно!'
                }
                failure {
                    echo 'Тесты завершились с ошибками'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Сборка Docker образа...'
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        stage('Push to Registry') {
            steps {
                echo 'Публикация образа в Docker Hub...'
                script {
                    docker.withRegistry('', 'docker-hub-credentials') {
                        docker.image("${DOCKER_IMAGE}").push()
                        docker.image("${DOCKER_IMAGE}").push('latest')
                    }
                }
            }
        }

        stage('Deploy to Dev') {
            when {
                expression { params.ENVIRONMENT == 'dev' }
            }
            steps {
                echo 'Развертывание в Dev...'
                script {
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    sh """
                        docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 8081:5000 \
                        -e STUDENT_NAME='${params.STUDENT_NAME}' \
                        ${DOCKER_IMAGE}
                    """
                }
                echo "Приложение доступно на порту 8081"
            }
        }

        stage('Deploy to Staging') {
            when {
                expression { params.ENVIRONMENT == 'staging' }
            }
            steps {
                echo 'Развертывание в Staging...'
                script {
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    sh """
                        docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 8082:5000 \
                        -e STUDENT_NAME='${params.STUDENT_NAME}' \
                        ${DOCKER_IMAGE}
                    """
                }
                echo "Приложение доступно на порту 8082"
            }
        }

        stage('Approve Production') {
            when {
                expression { params.ENVIRONMENT == 'production' }
            }
            steps {
                input message: 'Подтвердите развертывание в PRODUCTION?', ok: 'Да, развернуть'
            }
        }

        stage('Deploy to Production') {
            when {
                expression { params.ENVIRONMENT == 'production' }
            }
            steps {
                echo 'Развертывание в Production...'
                script {
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    sh """
                        docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 80:5000 \
                        -e STUDENT_NAME='${params.STUDENT_NAME}' \
                        ${DOCKER_IMAGE}
                    """
                }
                echo "Приложение доступно на порту 80"
            }
        }

        stage('Tag Release') {
            when {
                expression { params.ENVIRONMENT == 'production' }
            }
            steps {
                echo "Создание Git тега v${BUILD_NUMBER}..."
                withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh """
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins"
                        git tag -a v${BUILD_NUMBER} -m "Release version ${BUILD_NUMBER}"
                        git push https://${GIT_USER}:\${GIT_TOKEN}@github.com/GolubYaroslav/simple-python-app.git v${BUILD_NUMBER}
                    """
                }
                echo "Тег v${BUILD_NUMBER} успешно создан!"
            }
        }
    }

    post {
        always {
            echo 'Очистка рабочего пространства...'
            cleanWs()
        }
        success {
            echo "Пайплайн успешно выполнен для окружения ${params.ENVIRONMENT}!"
        }
        failure {
            echo 'Пайплайн завершился с ошибкой. Проверьте логи.'
        }
    }
}
