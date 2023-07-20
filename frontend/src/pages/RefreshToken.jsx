import { commitMutation, graphql } from "react-relay";
import environment from "../relayEnvironment";

const refreshTokenMutation = graphql`
  mutation RefreshTokenMutation($token: String!) {
    refreshToken(input: { token: $token }) {
      token
      clientMutationId
      payload
      refreshExpiresIn
    }
  }
`;

export function performRefreshTokenMutation(router) {
    const variables = {
        token: localStorage.jwt,
    };

    commitMutation(environment, {
        mutation: refreshTokenMutation,
        variables,
        onCompleted: ({ refreshToken }, errors) => {
            if (errors) {
                localStorage.jwt = '';
                router.replace("/login/");
            } else if (refreshToken) {
                localStorage.jwt = refreshToken.token;
            }
        },
        onError: (error) => {
            localStorage.jwt = '';
            router.replace("/login/");
        },
    });
}

export function getImageData(imageUrl) {
    const mediaUrl = import.meta.env.VITE_DJANGO_MEDIA_URL + imageUrl
    return fetch(mediaUrl, {
        headers: {
            'Authorization': 'Bearer ' + localStorage.jwt,
        },
    }).then(function (response) {
        return response.text();
    }).then((response) => {
        return `data:image;base64,${response}`;
    }).catch((error) => {
        // eslint-disable-next-line no-console
        console.log(error);
    });
}
