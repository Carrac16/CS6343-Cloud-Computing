# CS6343
Repository to work on project workflow

## Docker service commands
- Workflow manager

   * docker service create -dt --constraint node.role==manager --network attachable_overlay_network --name workflowmanager --mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock -p 6000:6000 kbouguyon/workflow_manager

- Email Client

   * docker run --rm -it -v <path to workflow.json>:/workflow.json --network attachable_overlay_network matthewp76/emailclient <# emails> <workflow id (optional)>


## Database commands

- Clear database

   * curl http://cluster5-2.utdallas.edu:8080/api/clearTable

- Run cassandra database

   * Docker ps - a
   * Docker start 91a2b9fa9071

- To check cassandra on multiple nodes

   * Docker exec -ti cassandra_test4 nodetool status
