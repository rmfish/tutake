import {Card, Badge, Group, Anchor, Text, Button, Grid, Flex, Breadcrumbs, Divider} from "@mantine/core";
import {Component} from "react";
import axios from "axios";

const jobs = [{name: "test"}, {name: "2"}, {name: "3"}, {name: "4"}]

class IndexPage extends Component<any, any> {
    constructor(props: any) {
        super(props);

        this.state = {
            jobs: [],
        };
    }

    componentDidMount() {
        console.log("componentDidMount")
        axios.get('http://127.0.0.1:5000/api/jobs').then((response) => {
            console.log("api invoke" + response.data)
            this.setState({jobs: response.data});
        });
    }

    render() {
        return <Grid p="50px">
            {this.state.jobs.map((job: any) => (
                // eslint-disable-next-line react/jsx-key
                <Grid.Col xs={6} sm={4} md={4} lg={3} xl={3}>
                    <Card shadow="sm" miw="200px" maw="350px" m="xl" radius="xs" withBorder pt="md">
                        <Card.Section pt="md">
                            <Group position="left" spacing='xs'>
                                <Text mx="md" mb="0px" weight={500}>{job.api.title}</Text>
                                <Text mx="md" mb="0px" size="xs" inline>{job.job.id}</Text>
                                <Breadcrumbs mx="md" my='0px'
                                             color='gray'>{job.api.path.slice(1, -1).map((path: any, index: any) => (
                                    <Text size="xs" key={index}>{path[1]}</Text>
                                ))}</Breadcrumbs>
                            </Group>
                        </Card.Section>
                        <Divider my="5px" mx="0px"/>
                        <Flex gap="xs" justify="flex-start" align="flex-start" direction="column">
                            <Group position="left" spacing='xs' my="0px"> <Text fw={500} fz="xs">描述:</Text><Text
                                fz="xs">{job.api.desc}</Text></Group>
                            {/*<Badge variant="gradient"*/}
                            {/*       gradient={{from: 'indigo', to: 'cyan'}}>{job.job.next_run_time}</Badge>*/}
                            {/*<Text fz="xs">{job.job.next_run_time}</Text>*/}
                            <Group position="left" spacing='xs' my="0px"> <Text fw={500}
                                                                                fz="xs">{job.job.trigger}:</Text>
                                <Text fz="xs">{job.job.minute} </Text>
                                <Text fz="xs">{job.job.hour} </Text>
                                <Text fz="xs">{job.job.day} </Text>
                                <Text fz="xs">{job.job.month} </Text>
                                <Text fz="xs">{job.job.day_of_week} </Text>
                            </Group>
                            <Group position="left" spacing='xs' my="0px"> <Text fw={500}
                                                                                fz="xs">下次执行时间:</Text><Text
                                fz="xs">{job.job.next_run_time}</Text></Group>
                        </Flex>
                        <Button variant="light" color="blue" fullWidth mt="md" radius="md">
                            Book classic tour now
                        </Button>
                    </Card></Grid.Col>
            ))}
        </Grid>;
    }
}

export default IndexPage