package vision.ocean.helpers;

import android.util.Log;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.CookieStore;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.widget.ImageView;

import java.io.IOException;

public final class MyHttpClient {

    // Set the timeout in milliseconds until a connection is established.
    // The default value is zero, that means the timeout is not used.
    private final static int TIMEOUT_CONNECTION = 3000;
    // Set the default socket timeout (SO_TIMEOUT)
    // in milliseconds which is the timeout for waiting for data.
    private final static int TIMEOUT_SOCKET = 0;

    // Based on given request, download data and cookies from web service.
    static String runRequestWithCookies(HttpUriRequest request, CookieStore cookieStore) {
        HttpParams httpParameters = new BasicHttpParams();
        HttpConnectionParams.setConnectionTimeout(httpParameters, TIMEOUT_CONNECTION);
        HttpConnectionParams.setSoTimeout(httpParameters, TIMEOUT_SOCKET);

        DefaultHttpClient httpClient = new DefaultHttpClient(httpParameters);
        httpClient.setCookieStore(cookieStore);

        ResponseHandler<String> handler = new BasicResponseHandler();
        String response = null;
        try {
            response = httpClient.execute(request, handler);
        } catch (ClientProtocolException e) {
            Log.e("ClientProtocolException", e.toString());
            e.printStackTrace();
        } catch (IOException e) {
            Log.e("IOException", e.toString());
            e.printStackTrace();
        }

        return response;
    }

    // Based on given request, download data from web service and return it as simple String.
    static public String runRequest(HttpUriRequest request) {
        HttpParams httpParameters = new BasicHttpParams();
        HttpConnectionParams.setConnectionTimeout(httpParameters, TIMEOUT_CONNECTION);
        HttpConnectionParams.setSoTimeout(httpParameters, TIMEOUT_SOCKET);

        DefaultHttpClient httpClient = new DefaultHttpClient(httpParameters);

        ResponseHandler<String> handler = new BasicResponseHandler();
        String response = null;
        try {
            response = httpClient.execute(request, handler);
        } catch (ClientProtocolException e) {
            Log.e("ClientProtocolException", e.toString());
            e.printStackTrace();
        } catch (IOException e) {
            Log.e("IOException", e.toString());
            e.printStackTrace();
        }

        return response;
    }

    // Based on given request, download data from web service and return it as simple String.
    static public String runJsonRequest(HttpUriRequest request) {
        // Sets a request header so the service receiving the request.
        request.setHeader("Accept", "application/json");
        request.setHeader("Content-type", "application/json");

        HttpParams httpParameters = new BasicHttpParams();
        HttpConnectionParams.setConnectionTimeout(httpParameters, TIMEOUT_CONNECTION);
        HttpConnectionParams.setSoTimeout(httpParameters, TIMEOUT_SOCKET);

        DefaultHttpClient httpClient = new DefaultHttpClient(httpParameters);

        ResponseHandler<String> handler = new BasicResponseHandler();
        String response = null;
        try {
            response = httpClient.execute(request, handler);
        } catch (ClientProtocolException e) {
            Log.e("ClientProtocolException", e.toString());
            e.printStackTrace();
        } catch (IOException e) {
            Log.e("IOException", e.toString());
            e.printStackTrace();
        }

        return response;
    }

    // Parse returned String to JsonArray, if possible.
    static public JSONArray getJSONArray(HttpUriRequest request) {
        JSONArray jsonArray = null;
        try {
            jsonArray = new JSONArray(runJsonRequest(request));
        } catch (JSONException e) {
            Log.e("JSONException", e.toString());
            e.printStackTrace();
        }

        return jsonArray;
    }

    // Parse returned String to JsonObject, if possible.
    static public JSONObject getJSONObjectWithCookies(HttpUriRequest request, CookieStore cookieStore) {
        JSONObject jsonObject = null;
        try {
            jsonObject = new JSONObject(runRequestWithCookies(request, cookieStore));
        } catch (JSONException e) {
            Log.e("JSONException", e.toString());
            e.printStackTrace();
        }

        return jsonObject;
    }

    // Parse returned String to JsonObject, if possible.
    static public JSONObject getJSONObject(HttpUriRequest request) {
        JSONObject jsonObject = null;
        try {
            jsonObject = new JSONObject(runJsonRequest(request));
        } catch (JSONException e) {
            Log.e("JSONException", e.toString());
            e.printStackTrace();
        }

        return jsonObject;
    }

    // Creates Bitmap from InputStream and returns it
    static public Bitmap downloadImage(String url) {
        Bitmap bitmap = null;
        InputStream stream = null;
        BitmapFactory.Options bmOptions = new BitmapFactory.Options();
        bmOptions.inSampleSize = 1;

        try {
            stream = getHttpConnection(url);
            bitmap = BitmapFactory.
                    decodeStream(stream, null, bmOptions);
            stream.close();
        } catch (IOException e1) {
            e1.printStackTrace();
        }
        return bitmap;
    }

    // Makes HttpURLConnection and returns InputStream
    static private InputStream getHttpConnection(String urlString)
            throws IOException {
        InputStream stream = null;
        URL url = new URL(urlString);
        URLConnection connection = url.openConnection();

        try {
            HttpURLConnection httpConnection = (HttpURLConnection) connection;
            httpConnection.setRequestMethod("GET");
            httpConnection.connect();

            if (httpConnection.getResponseCode() == HttpURLConnection.HTTP_OK) {
                stream = httpConnection.getInputStream();
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
        return stream;
    }
}
