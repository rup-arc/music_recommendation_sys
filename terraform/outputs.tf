output "s3_data_bucket" {
  value = aws_s3_bucket.data_bucket.id
}

output "cluster_name" {
  value = aws_eks_cluster.cluster.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.cluster.endpoint
}

output "configure_kubectl" {
  value = "aws eks update-kubeconfig --name ${aws_eks_cluster.cluster.name} --region ${var.aws_region}"
}

output "upload_csv_command" {
  value = "aws s3 cp songs.csv s3://${aws_s3_bucket.data_bucket.id}/csv/songs.csv"
}