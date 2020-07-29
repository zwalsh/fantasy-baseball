pipeline {
    agent any
    stages {
        stage('test') {
            steps {
                sh 'python3.8 -m unittest'
            }
        }
        stage('lint') {
            steps {
                sh 'find . -type f -name "*.py" | xargs pylint'
            }
        }
    }
}